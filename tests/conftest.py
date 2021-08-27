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
    body="",
    headers=CIMultiDict({"Content-Type": "application/json"}),
    uri_params={},
    method="GET",  # pylint issue #214
    query_params=None,
    context={},
    stage_vars={},
    is_base64_encoded=False,
    user=None,
)


@pytest.fixture(autouse=True)
def sample_request():
    return req


@pytest.fixture(autouse=True)
def sample_event():
    return Event(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body=req,
    )


def _base_auth_payload():
    return {
        "allow": {"*": "*"},
        "deny": {},
        "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "test-issuer",
    }


@pytest.fixture(autouse=True)
def base_auth_payload():
    return _base_auth_payload()


a_header = Authorizer.sign_authz(
    {**_base_auth_payload(), "allow": {"test_res": {"perm-name": {"allow": "*"}}}, "deny": {}},
    SAMPLE_PRIVATE_KEY
)

@pytest.fixture(autouse=True)
def auth_header():
    return a_header


username = str(uuid4())
cognito_user = {
    "cognito:username": username,
    "custom:id": str(uuid4()),
    "email": f"{str(uuid4())}@{str(uuid4())}.com",
    "custom:1": str(uuid4()),
    "custom:2": str(uuid4()),
    "custom:3": str(uuid4()),
    "custom:4": str(uuid4()),
    "custom:5": str(uuid4()),
    "aud": allowed_audiences[0],
}
token = encode_token(cognito_user)

with patch("lbz.jwt_utils.PUBLIC_KEYS", [SAMPLE_PUBLIC_KEY]), patch(
        "lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences
):
    def_user = User(token)


@pytest.fixture(autouse=True)
def user_token():
    return token


@pytest.fixture(autouse=True)
def user_username():
    return username


@pytest.fixture(autouse=True)
def user_cogniot():
    return cognito_user


@pytest.fixture(autouse=True)
def user():
    return def_user
