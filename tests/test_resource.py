import json
import logging
from collections import defaultdict
from http import HTTPStatus
from os import environ
from typing import Any, Callable, Dict, List
from unittest.mock import ANY, MagicMock, patch

from jose import jwt
from multidict import CIMultiDict
from pytest import LogCaptureFixture

from lbz.authentication import User
from lbz.collector import AuthzCollector
from lbz.dev.misc import APIGatewayEvent
from lbz.events.api import EventAPI
from lbz.exceptions import NotFound, ServerError
from lbz.misc import MultiDict
from lbz.request import Request
from lbz.resource import (
    ALLOW_ORIGIN_HEADER,
    CORSResource,
    EventAwareResource,
    PaginatedCORSResource,
    Resource,
)
from lbz.response import Response
from lbz.router import Router, add_route
from tests.fixtures.rsa_pair import SAMPLE_PUBLIC_KEY

# TODO: Use fixtures yielded from conftest.py

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

event = APIGatewayEvent(
    resource_path="/",
    method="GET",
    body=req,  # pylint issue #214
    headers={},
    path_params={},
    query_params={},
)

event_wrong_uri = APIGatewayEvent(
    resource_path="/xxxs/asdasd/xxx",
    method="GET",
    headers={},
    path_params={},
    query_params={},
    body=req,
)


class TestResource:
    def setup_method(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.res = Resource(event)

    def test___init__(self) -> None:
        assert isinstance(self.res.path, str)
        assert self.res.path == "/"
        assert isinstance(self.res.method, str)
        assert self.res.method == "GET"
        assert self.res.path_params == {}
        assert isinstance(self.res.request, Request)
        assert self.res._router is not None  # pylint: disable=protected-access
        assert isinstance(self.res._router, Router)  # pylint: disable=protected-access
        assert self.res.request.user is None
        assert isinstance(
            self.res._authz_collector, AuthzCollector  # pylint: disable=protected-access
        )

    def test_get_all_possible_authz(self) -> None:
        assert self.res.get_authz_data() == {
            "resource": {
                "possible_permissions": {},
                "guest_permissions": {},
            }
        }

    @patch.object(Resource, "_get_user")
    def test___call__(self, get_user: MagicMock) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response({"message": "x"})

        cls = XResource(event)
        resp = cls()
        assert isinstance(resp, Response), resp
        assert resp.to_dict() == {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 200,
            "body": '{"message":"x"}',
            "isBase64Encoded": False,
        }
        get_user.assert_called_once_with({})

    def test_not_found_returned_when_path_not_defined(self) -> None:
        response = Resource(event_wrong_uri)()
        assert isinstance(response, Response)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_request_id_added_when_frameworks_exception_raised(self) -> None:
        class TestAPI(Resource):
            @add_route("/")
            def test_method(self) -> None:
                raise NotFound

        response = TestAPI(event)()

        assert response.body == {
            "message": NotFound.message,
            "request_id": event["requestContext"]["requestId"],
        }

    def test___repr__(self) -> None:
        self.res.urn = "/foo/id-12345/bar"
        assert str(self.res) == "<Resource GET @ /foo/id-12345/bar >"

    def test_unauthorized_when_authentication_not_configured(self) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("x")

        resp = XResource({**event, "headers": {"authentication": "dummy"}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.object(User, "__init__", return_value=None)
    def test_user_loaded_when_cognito_authentication_configured_correctly(
        self, load_user: MagicMock
    ) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("x")

        key_id = SAMPLE_PUBLIC_KEY["kid"]
        authentication_token = jwt.encode({"username": "x"}, "", headers={"kid": key_id})

        XResource({**event, "headers": {"authentication": authentication_token}})()
        load_user.assert_called_once_with(authentication_token)

    def test_unauthorized_when_jwt_header_lacks_kid(self) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("x")

        authentication_token = jwt.encode({"foo": "bar"}, "")
        resp = XResource({**event, "headers": {"authentication": authentication_token}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_unauthorized_when_no_matching_key_in_env_variable(self) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("x")

        authentication_token = jwt.encode({"kid": "foobar"}, "")
        resp = XResource({**event, "headers": {"authentication": authentication_token}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_unauthorized_when_jwt_header_malformed(self) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("x")

        resp = XResource({**event, "headers": {"authentication": "12345"}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_pre_request_hook(self) -> None:
        pre_request_called = False

        class TestAPI(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("OK")

            def pre_request_hook(self) -> None:
                nonlocal pre_request_called
                pre_request_called = True

        response = TestAPI(event)()

        assert response.body == "OK"
        assert pre_request_called

    def test_post_request_hook(self) -> None:
        post_request_called = False

        class TestAPI(Resource):
            @add_route("/")
            def test_method(self) -> None:
                raise ServerError("test")

            def post_request_hook(self) -> None:
                nonlocal post_request_called
                post_request_called = True

        response = TestAPI(event)()

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert post_request_called

    def test_post_request_hook_fails_but_response_is_still_sent(
        self, caplog: LogCaptureFixture
    ) -> None:
        class TestAPI(Resource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response("OK")

            def post_request_hook(self) -> None:
                raise TypeError("xxx")

        response = TestAPI(event)()

        assert response.status_code == HTTPStatus.OK
        assert caplog.record_tuples == [
            (
                "lbz.resource",
                logging.ERROR,
                "xxx",
            )
        ]

    def test_500_returned_when_server_error_caught(self) -> None:
        class XResource(Resource):
            @add_route("/")
            def test_method(self) -> None:
                raise RuntimeError("test")

        resp = XResource(event)()
        assert isinstance(resp, Response), resp
        assert resp.to_dict() == {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 500,
            "body": ANY,
            "isBase64Encoded": False,
        }
        assert json.loads(resp.to_dict()["body"]) == {
            "message": "Server got itself in trouble",
            "request_id": ANY,
        }

    def test__get_name__uses_custom_name_attribute(self) -> None:
        class XResource(Resource):
            _name = "test"

        assert XResource.get_name() == "test"

    def test__get_name__uses_class_name_attribute_when_custom_name_is_not_defined(self) -> None:
        class XResource(Resource):
            pass

        assert XResource.get_name() == "xresource"


ORIGIN_LOCALHOST = "http://localhost:3000"
ORIGIN_EXAMPLE = "https://api.example.com"


class TestCORSResource:
    def setup_method(self) -> None:
        environ["CORS_ORIGIN"] = f"{ORIGIN_LOCALHOST},{ORIGIN_EXAMPLE}"

    def teardown_method(self) -> None:
        del environ["CORS_ORIGIN"]

    def make_cors_handler(
        self, origins: List[str] = None, req_origin: str = None, cors_headers: list = None
    ) -> CORSResource:
        an_event: Dict[Any, MagicMock] = defaultdict(MagicMock())
        an_event["headers"] = {"origin": req_origin} if req_origin is not None else {}
        cors_handler = CORSResource(
            an_event, ["GET", "POST"], origins=origins, cors_headers=cors_headers
        )
        return cors_handler

    def test_cors_origin_headers_from_env_are_correct_1(self) -> None:
        assert self.make_cors_handler().resp_headers_json[ALLOW_ORIGIN_HEADER] == ORIGIN_LOCALHOST

    def test_cors_origin_headers_from_env_are_correct_2(self) -> None:
        headers = self.make_cors_handler(req_origin=ORIGIN_EXAMPLE).resp_headers_json[
            ALLOW_ORIGIN_HEADER
        ]
        assert headers == ORIGIN_EXAMPLE

    def test_cors_origin_headers_from_env_are_correct_3(self) -> None:
        headers = self.make_cors_handler(req_origin="invalid_origin").resp_headers_json[
            ALLOW_ORIGIN_HEADER
        ]
        assert headers == ORIGIN_LOCALHOST

    def test_cors_origin_headers_from_param_are_correct(self) -> None:
        origin_headers = [ORIGIN_LOCALHOST, ORIGIN_EXAMPLE]
        cors_handler = self.make_cors_handler(origins=origin_headers, req_origin=ORIGIN_EXAMPLE)
        assert cors_handler.resp_headers_json[ALLOW_ORIGIN_HEADER] == ORIGIN_EXAMPLE

    def test_cors_origin_headers_from_wildcard(self) -> None:
        cors_handler = self.make_cors_handler(
            origins=["https://*.lb.com"], req_origin="https://dev.test.lb.com"
        )
        assert cors_handler.resp_headers_json[ALLOW_ORIGIN_HEADER] == "https://dev.test.lb.com"

    def test_cors_origin_headers_from_wildcard_no_orgin(self) -> None:
        cors_handler = self.make_cors_handler(req_origin=None).resp_headers_json[
            ALLOW_ORIGIN_HEADER
        ]
        assert cors_handler == "http://localhost:3000"

    def test_cors_origin_headers_from_wildcard_star(self) -> None:
        assert self.make_cors_handler(origins=["*"]).resp_headers_json[ALLOW_ORIGIN_HEADER] == "*"
        cors_handler = self.make_cors_handler(origins=["*"], req_origin="http://localhost:3000")
        assert cors_handler.resp_headers_json[ALLOW_ORIGIN_HEADER] == "*"

    def test_all_headers(self) -> None:
        content_type = "image/jpeg"

        assert self.make_cors_handler().resp_headers(content_type) == {
            "Access-Control-Allow-Headers": (
                "Content-Type, X-Amz-Date, Authentication, "
                "Authorization, X-Api-Key, X-Amz-Security-Token"
            ),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_LOCALHOST,
            "Content-Type": content_type,
        }

    def test_resp_headers_json(self) -> None:
        assert self.make_cors_handler().resp_headers_json["Content-Type"] == "application/json"

    def test_resp_headers_no_content_type_by_default(self) -> None:
        assert self.make_cors_handler().resp_headers().get("Content-Type") is None

    def test_options_request(self) -> None:
        inst = self.make_cors_handler(req_origin=ORIGIN_EXAMPLE)
        inst.method = "OPTIONS"
        assert inst().headers == {
            "Access-Control-Allow-Headers": ", ".join(
                CORSResource._cors_headers  # pylint: disable=protected-access
            ),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_EXAMPLE,
        }

    def test_cors_headers_param_request(self) -> None:
        inst = self.make_cors_handler(req_origin=ORIGIN_EXAMPLE, cors_headers=["X-PRN-KEY"])
        inst.method = "OPTIONS"
        assert inst().headers == {
            "Access-Control-Allow-Headers": (
                "Content-Type, X-Amz-Date, Authentication, Authorization, X-Api-Key, "
                "X-Amz-Security-Token, X-PRN-KEY"
            ),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_EXAMPLE,
        }

    @patch.dict(environ, {"CORS_HEADERS": "X-PRN-KEY,X-PRN-TOKEN"})
    def test_cors_headers_env_request(self) -> None:
        inst = self.make_cors_handler(req_origin=ORIGIN_EXAMPLE)
        inst.method = "OPTIONS"
        assert inst().headers == {
            "Access-Control-Allow-Headers": (
                "Content-Type, X-Amz-Date, Authentication, Authorization, "
                "X-Api-Key, X-Amz-Security-Token, X-PRN-KEY, X-PRN-TOKEN"
            ),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_EXAMPLE,
        }

    @patch.dict(environ, {"CORS_HEADERS": "X-PRN-KEY,X-PRN-TOKEN"})
    def test_cors_headers_param_more_important_than_env_request(self) -> None:
        inst = self.make_cors_handler(req_origin=ORIGIN_EXAMPLE, cors_headers=["X-PRN-XXX"])
        inst.method = "OPTIONS"
        assert inst().headers == {
            "Access-Control-Allow-Headers": (
                "Content-Type, X-Amz-Date, Authentication, Authorization, "
                "X-Api-Key, X-Amz-Security-Token, X-PRN-XXX"
            ),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_EXAMPLE,
        }


class TestPagination:
    @patch.object(PaginatedCORSResource, "__init__", return_value=None)
    def setup_method(self, _test_method: Callable, _init_mock: MagicMock) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.resource = PaginatedCORSResource({}, [])
        self.resource.path = "/test/path"
        self.resource.urn = "/test/path"
        req.query_params = MultiDict(
            {
                "test": ["param"],
                "another": ["example"],
            }
        )
        self.resource.request = req

    def test_get_pagination(self) -> None:
        expected_prefix = "/test/path?test=param&another=example"
        assert self.resource.get_pagination(total_items=100, offset=20, limit=10) == {
            "count": 100,
            "links": {
                "current": f"{expected_prefix}&offset=20&limit=10",
                "last": f"{expected_prefix}&offset=90&limit=10",
                "next": f"{expected_prefix}&offset=30&limit=10",
                "prev": f"{expected_prefix}&offset=10&limit=10",
            },
        }

    def test_get_pagination_multifield_query_params(self) -> None:
        expected_prefix = "/test/path?test=param&another=example&another=example2"
        req.query_params = MultiDict(
            {
                "test": ["param"],
                "another": ["example", "example2"],
            }
        )
        self.resource.request = req

        assert self.resource.get_pagination(total_items=100, offset=20, limit=10) == {
            "count": 100,
            "links": {
                "current": f"{expected_prefix}&offset=20&limit=10",
                "last": f"{expected_prefix}&offset=90&limit=10",
                "next": f"{expected_prefix}&offset=30&limit=10",
                "prev": f"{expected_prefix}&offset=10&limit=10",
            },
        }

    def test_no_prev_link_when_offset_minus_limit_lt_zero(self) -> None:
        links = self.resource.get_pagination(total_items=100, offset=10, limit=20)["links"]
        assert "prev" not in links

    def test_no_next_returned_when_offset_plus_limit_gt_total_items(self) -> None:
        links = self.resource.get_pagination(total_items=25, offset=20, limit=10)["links"]
        assert "next" not in links

    def test_pagination_uri_with_existing_pagination_query_params(self) -> None:
        self.resource.request.query_params = MultiDict({"offset": "3", "limit": "42"})
        expected = "/test/path?offset={offset}&limit={limit}"
        assert self.resource._pagination_uri == expected  # pylint: disable=protected-access

    def test_pagination_uri_without_query_params(self) -> None:
        self.resource.request.query_params = MultiDict({})
        expected = "/test/path?offset={offset}&limit={limit}"
        assert self.resource._pagination_uri == expected  # pylint: disable=protected-access


class TestEventAwareResource:
    def test_check_if_init_creates_event_api_attribute(self) -> None:
        class XResource(EventAwareResource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response({"message": "x"})

        res = XResource(event)
        assert res.event_api is EventAPI()

    @patch.object(EventAPI, "clear")
    @patch.object(EventAPI, "send")
    def test_post_hook_event_api_sent(
        self, mocked_event_api_send: MagicMock, mocked_event_api_clear: MagicMock
    ) -> None:
        class XResource(EventAwareResource):
            @add_route("/")
            def test_method(self) -> Response:
                return Response({"message": "x"})

        XResource(event)()

        mocked_event_api_clear.assert_called_once()
        mocked_event_api_send.assert_called_once()

    @patch.object(EventAPI, "clear")
    @patch.object(EventAPI, "clear_pending")
    @patch.object(EventAPI, "send")
    def test_post_hook_event_api_was_not_sent_when_response_with_error(
        self,
        mocked_event_api_send: MagicMock,
        mocked_event_api_clear_pending: MagicMock,
        mocked_event_api_clear: MagicMock,
    ) -> None:
        class XResource(EventAwareResource):
            @add_route("/")
            def test_method(self) -> None:
                raise TypeError

        XResource(event)()

        mocked_event_api_send.assert_not_called()
        mocked_event_api_clear.assert_called_once_with()
        mocked_event_api_clear_pending.assert_called_once_with()
