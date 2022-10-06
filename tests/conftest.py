# coding=utf-8
import os
from datetime import datetime, timedelta
from typing import Any, Iterator, List, Type
from uuid import uuid4

import pytest
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.authz.authorizer import Authorizer
from lbz.authz.decorators import authorization
from lbz.collector import authz_collector
from lbz.configuration import ConfigValue
from lbz.dev.misc import APIGatewayEvent
from lbz.request import Request
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import Router, add_route
from tests import SAMPLE_PRIVATE_KEY
from tests.utils import encode_token


class MockedConfig(ConfigValue):
    def getter(self) -> Any:
        return self._key


@pytest.fixture(scope="session", name="allowed_audiences")
def allowed_audiences_fixture() -> List[str]:
    return os.environ["ALLOWED_AUDIENCES"].split(",")


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


@pytest.fixture(scope="session", name="user")
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
