# coding=utf-8
from datetime import datetime, timedelta
from typing import List
import os
from uuid import uuid4

import pytest
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.authz.authorizer import Authorizer
from lbz.dev.misc import Event
from lbz.request import Request
from tests import SAMPLE_PRIVATE_KEY
from tests.utils import encode_token


@pytest.fixture(scope="session")
def allowed_audiences() -> List[str]:
    return os.environ["ALLOWED_AUDIENCES"].split(",")


@pytest.fixture()
def sample_request() -> Request:
    # TODO: change to simple factory / parametrise it
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
def sample_event() -> Event:
    return Event(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body={},
    )


@pytest.fixture(scope="session")
def full_access_authz_payload() -> dict:
    return {
        "allow": {"*": "*"},
        "deny": {},
        "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "test-issuer",
    }


@pytest.fixture(scope="session")
def full_access_auth_header(
    full_access_authz_payload,  # pylint: disable=redefined-outer-name
) -> str:
    return Authorizer.sign_authz(
        full_access_authz_payload,
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session")
def limited_access_auth_header(
    full_access_authz_payload,  # pylint: disable=redefined-outer-name
) -> str:
    return Authorizer.sign_authz(
        {
            **full_access_authz_payload,
            "allow": {"test_res": {"perm-name": {"allow": "*"}}},
            "deny": {},
        },
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session")
def username() -> str:
    return str(uuid4())


@pytest.fixture(scope="session")
def user_cognito(username) -> dict:  # pylint: disable=redefined-outer-name

    return {
        "cognito:username": username,
        "custom:id": str(uuid4()),
        "email": f"{str(uuid4())}@{str(uuid4())}.com",
        "custom:1": str(uuid4()),
        "custom:2": str(uuid4()),
        "custom:3": str(uuid4()),
        "custom:4": str(uuid4()),
        "custom:5": str(uuid4()),
        "aud": os.environ["ALLOWED_AUDIENCES"].split(",")[0],
    }


@pytest.fixture(scope="session")
def user_token(user_cognito) -> str:  # pylint: disable=redefined-outer-name
    return encode_token(user_cognito)


@pytest.fixture(scope="session")
def user(user_token) -> User:  # pylint: disable=redefined-outer-name
    return User(user_token)


@pytest.fixture()
def sample_request_with_user(user) -> Request:  # pylint: disable=redefined-outer-name
    return Request(
        method="GET",
        body="",
        headers=CIMultiDict({"Content-Type": "application/json"}),
        context={},
        user=user,
        stage_vars={},
        is_base64_encoded=False,
        uri_params={},
    )
