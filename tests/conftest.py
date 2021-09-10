# coding=utf-8
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.authz.authorizer import Authorizer
from lbz.dev.misc import Event
from lbz.request import Request
from tests import SAMPLE_PRIVATE_KEY
from tests.fixtures.rsa_pair import SAMPLE_PUBLIC_KEY
from tests.utils import encode_token, allowed_audiences

req = Request(
    method="GET",
    body="",
    headers=CIMultiDict({"Content-Type": "application/json"}),
    user=None,
    uri_params={},
    context={},
    query_params=None,
    stage_vars={},
    is_base64_encoded=False,
)


@pytest.fixture()
def sample_request() -> Request:
    return req


@pytest.fixture()
def sample_event() -> Event:
    return Event(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body=req.to_dict(),
    )


def _base_auth_payload() -> dict:
    return {
        "allow": {"*": "*"},
        "deny": {},
        "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "test-issuer",
    }


@pytest.fixture()
def base_auth_payload() -> dict:
    return _base_auth_payload()


AUTH_HEADER = Authorizer.sign_authz(
    {**_base_auth_payload(), "allow": {"test_res": {"perm-name": {"allow": "*"}}}, "deny": {}},
    SAMPLE_PRIVATE_KEY,
)


@pytest.fixture()
def auth_header() -> str:
    return AUTH_HEADER


USERNAME = str(uuid4())
COGNITO_USER = {
    "cognito:username": USERNAME,
    "custom:id": str(uuid4()),
    "email": f"{str(uuid4())}@{str(uuid4())}.com",
    "custom:1": str(uuid4()),
    "custom:2": str(uuid4()),
    "custom:3": str(uuid4()),
    "custom:4": str(uuid4()),
    "custom:5": str(uuid4()),
    "aud": allowed_audiences[0],
}
TOKEN = encode_token(COGNITO_USER)

with patch("lbz.jwt_utils.PUBLIC_KEYS", [SAMPLE_PUBLIC_KEY]), patch(
    "lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences
):
    USER = User(TOKEN)


@pytest.fixture()
def user_token() -> str:
    return TOKEN


@pytest.fixture()
def user_username() -> str:
    return USERNAME


@pytest.fixture()
def user_cogniot() -> dict:
    return COGNITO_USER


@pytest.fixture()
def user() -> User:
    return USER
