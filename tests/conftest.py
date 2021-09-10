# coding=utf-8
# pylint: disable=redefined-outer-name
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


@pytest.fixture()
def sample_request() -> Request:
    return Request(
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
def sample_event(sample_request) -> Event:
    return Event(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body=sample_request.to_dict(),
    )


def _base_auth_payload() -> dict:
    return {
        "allow": {"*": "*"},
        "deny": {},
        "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "test-issuer",
    }


@pytest.fixture(scope="session")
def base_auth_payload() -> dict:
    return _base_auth_payload()


@pytest.fixture(scope="session")
def auth_header() -> str:
    return Authorizer.sign_authz(
        {**_base_auth_payload(), "allow": {"test_res": {"perm-name": {"allow": "*"}}}, "deny": {}},
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session")
def user_username() -> str:
    return str(uuid4())


@pytest.fixture(scope="session")
def user_cognito(user_username) -> dict:
    return {
        "cognito:username": user_username,
        "custom:id": str(uuid4()),
        "email": f"{str(uuid4())}@{str(uuid4())}.com",
        "custom:1": str(uuid4()),
        "custom:2": str(uuid4()),
        "custom:3": str(uuid4()),
        "custom:4": str(uuid4()),
        "custom:5": str(uuid4()),
        "aud": allowed_audiences[0],
    }


@pytest.fixture(scope="session")
def user_token(user_cognito) -> str:
    return encode_token(user_cognito)


@pytest.fixture(scope="session")
def user(user_token) -> User:
    with patch("lbz.jwt_utils.PUBLIC_KEYS", [SAMPLE_PUBLIC_KEY]), patch(
        "lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences
    ):
        return User(user_token)
