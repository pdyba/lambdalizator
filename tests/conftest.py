import json
from datetime import datetime, timedelta
from os import environ
from typing import Iterator, List, Type
from unittest.mock import patch
from uuid import uuid4

import pytest
from multidict import CIMultiDict

from lbz._cfg import (
    ALLOWED_AUDIENCES,
    ALLOWED_ISS,
    ALLOWED_PUBLIC_KEYS,
    AUTH_REMOVE_PREFIXES,
    AWS_LAMBDA_FUNCTION_NAME,
    CORS_HEADERS,
    CORS_ORIGIN,
    EVENTS_BUS_NAME,
    LBZ_DEBUG_MODE,
    LOGGING_LEVEL,
)
from lbz.authentication import User
from lbz.authz.authorizer import Authorizer
from lbz.authz.decorators import authorization
from lbz.collector import authz_collector
from lbz.dev.misc import APIGatewayEvent
from lbz.request import Request
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import Router, add_route
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY, SAMPLE_PUBLIC_KEY
from tests.utils import encode_token


@pytest.fixture(scope="session", name="allowed_audiences")
def allowed_audiences_fixture() -> List[str]:
    return [str(uuid4()), str(uuid4())]


@pytest.fixture(autouse=True)
def setting_initial_lbz_configuration(allowed_audiences: List[str]) -> Iterator[None]:
    patched_environ = {
        "AUTH_REMOVE_PREFIXES": "1",
        "ALLOWED_PUBLIC_KEYS": json.dumps({"keys": [SAMPLE_PUBLIC_KEY]}),
        "ALLOWED_AUDIENCES": ",".join(allowed_audiences),
        "ALLOWED_ISS": "test-issuer",
        "AWS_LAMBDA_FUNCTION_NAME": "million-dollar-lambda",
        "EVENTS_BUS_NAME": "million-dollar-lambda-event-bus",
        "AWS_DEFAULT_REGION": "us-west-2",
    }
    with patch.dict(environ, patched_environ, clear=True):
        LBZ_DEBUG_MODE.reset()
        LOGGING_LEVEL.reset()
        CORS_HEADERS.reset()
        CORS_ORIGIN.reset()
        AWS_LAMBDA_FUNCTION_NAME.reset()
        EVENTS_BUS_NAME.reset()
        ALLOWED_PUBLIC_KEYS.reset()
        ALLOWED_AUDIENCES.reset()
        ALLOWED_ISS.reset()
        AUTH_REMOVE_PREFIXES.reset()
        yield


@pytest.fixture(autouse=True)
def clear_authz_collector() -> Iterator[None]:
    yield
    authz_collector.clean()


@pytest.fixture(autouse=True)
def clear_router_collector() -> Iterator[None]:
    yield
    Router().clear()


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
def sample_event() -> APIGatewayEvent:
    return APIGatewayEvent(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body={},
    )


@pytest.fixture(scope="session", name="jwt_partial_payload")
def jwt_partial_payload_fixture(allowed_audiences: List[str]) -> dict:
    return {
        "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "test-issuer",
        "aud": allowed_audiences[0],
    }


@pytest.fixture(scope="session", name="full_access_authz_payload")
def full_access_authz_payload_fixture(jwt_partial_payload: dict) -> dict:
    return {
        "allow": {"*": "*"},
        "deny": {},
        **jwt_partial_payload,
    }


@pytest.fixture(scope="session")
def full_access_auth_header(
    full_access_authz_payload: dict,
) -> str:
    return Authorizer.sign_authz(
        full_access_authz_payload,
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session")
def limited_access_auth_header(
    full_access_authz_payload: dict,
) -> str:
    return Authorizer.sign_authz(
        {
            **full_access_authz_payload,
            "allow": {"test_res": {"perm-name": {"allow": "*"}}},
            "deny": {},
        },
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session", name="username")
def username_fixture() -> str:
    return str(uuid4())


@pytest.fixture(scope="session", name="user_cognito")
def user_cognito_fixture(username: str, jwt_partial_payload: dict) -> dict:
    return {
        "cognito:username": username,
        "custom:id": str(uuid4()),
        "email": f"{str(uuid4())}@{str(uuid4())}.com",
        "custom:1": str(uuid4()),
        "custom:2": str(uuid4()),
        "custom:3": str(uuid4()),
        "custom:4": str(uuid4()),
        "custom:5": str(uuid4()),
        **jwt_partial_payload,
    }


@pytest.fixture(scope="session", name="user_token")
def user_token_fixture(user_cognito: dict) -> str:
    return encode_token(user_cognito)


@pytest.fixture(name="user")  # scope="session", - TODO: bring that back to reduce run time
def user_fixture(user_token: str) -> User:
    return User(user_token)


@pytest.fixture()
def sample_request_with_user(user: User) -> Request:
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


@pytest.fixture()
def sample_resource() -> Type[Resource]:
    """Be careful when doing any changes in this fixture"""

    class HelloWorld(Resource):
        @add_route("/", method="GET")
        def list(self) -> Response:
            return Response({"message": "HelloWorld"})

        @add_route("/t/{id}", method="GET")
        def get(self) -> Response:
            return Response({"message": "HelloWorld"})

    return HelloWorld


@pytest.fixture()
def sample_resource_with_authorization() -> Type[Resource]:
    """Be careful when doing any changes in this fixture - especially for Auth Collector"""

    class XResource(Resource):
        _name = "test_res"

        @add_route("/")
        @authorization("perm-name")
        def handler(self, restrictions: dict) -> Response:
            assert restrictions == {"allow": "*", "deny": None}
            return Response("x")

        @add_route("/garbage")
        @authorization()
        def garbage(self, restrictions: dict) -> Response:  # pylint: disable=unused-argument
            return Response("x")

    return XResource
