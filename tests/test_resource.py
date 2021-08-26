# coding=utf-8
import json
from collections import defaultdict
from http import HTTPStatus
from os import environ
from typing import List
from unittest.mock import patch, MagicMock, ANY

import pytest
from jose import jwt
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.authz.collector import AuthzCollector
from lbz.dev.misc import Event
from lbz.exceptions import NotFound, ServerError
from lbz.misc import MultiDict
from lbz.request import Request
from lbz.resource import (
    Resource,
    CORSResource,
    PaginatedCORSResource,
    ALLOW_ORIGIN_HEADER,
)
from lbz.response import Response
from lbz.router import Router
from lbz.router import add_route
from tests.fixtures.cognito_auth import env_mock

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

event = Event(
    resource_path="/",
    method="GET",
    body=req,  # pylint issue #214
    headers={},
    path_params={},
    query_params={},
)

event_wrong_uri = Event(
    resource_path="/xxxs/asdasd/xxx",
    method="GET",
    headers={},
    path_params={},
    query_params={},
    body=req,
)

event_wrong_method = Event(
    resource_path="/",
    method="" "PRINT",
    headers={},
    path_params={},
    query_params={},
    body=req,
)


class TestResourceInit:
    def setup_method(self):
        # pylint: disable=attribute-defined-outside-init
        self.res = Resource(event)

    def test___init__(self):
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

    # def test_get_all_possible_authz(self):
    # TODO: enable it with testing fixes
    # assert self.res.get_authz_data() == {
    #     "resource": {
    #         "possible_permissions": {},
    #         "guest_permissions": {},
    #     }
    # }

    def test___repr__(self):
        self.res.urn = "/foo/id-12345/bar"
        assert str(self.res) == "<Resource GET @ /foo/id-12345/bar >"


class TestResource:
    @patch.object(Resource, "_get_user")
    def test___call__(self, get_user: MagicMock):
        class XResource(Resource):
            @add_route("/")
            def test_method(self):
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

    def test_not_found_returned_when_path_not_defined(self):
        response = Resource(event_wrong_uri)()
        assert isinstance(response, Response)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_unsupported_method(self):
        res = Resource(event_wrong_method)()
        assert res.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_request_id_added_when_frameworks_exception_raised(self):
        class TestAPI(Resource):
            @add_route("/")
            def test_method(self):
                raise NotFound

        response = TestAPI(event)()

        assert response.body == {
            "message": NotFound.message,
            "request_id": event["requestContext"]["requestId"],
        }

    def test_pre_request_hook(self):
        pre_request_called = False

        class TestAPI(Resource):
            @add_route("/")
            def test_method(self):
                return Response("OK")

            def pre_request_hook(self):
                nonlocal pre_request_called
                pre_request_called = True

        response = TestAPI(event)()

        assert response.body == "OK"
        assert pre_request_called

    def test_post_request_hook(self):
        post_request_called = False

        class TestAPI(Resource):
            @add_route("/")
            def test_method(self):
                raise ServerError("test")

            def post_request_hook(self):
                nonlocal post_request_called
                post_request_called = True

        response = TestAPI(event)()

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert post_request_called

    def test_500_returned_when_server_error_caught(self):
        class XResource(Resource):
            @add_route("/")
            def test_method(self):
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

    def test_get_name_from__name_parameter(self):
        class XResource(Resource):
            _name = "test"

        assert XResource.get_name() == "test"

    def test_get_name_from__name__parameter(self):
        class XResource(Resource):
            pass

        assert XResource.get_name() == "xresource"


class TestResourceAuthentication:
    def setup_class(self):
        class XResource(Resource):
            @add_route("/")
            def test_method(self):
                return Response("x")

        self.res = XResource  # pylint: disable=attribute-defined-outside-init

    def test_unauthorized_when_authentication_not_configured(self):
        resp = self.res({**event, "headers": {"authentication": "dummy"}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.object(User, "__init__", return_value=None)
    def test_user_loaded_when_cognito_authentication_configured_correctly(
        self, load_user: MagicMock
    ):
        key = json.loads(env_mock["ALLOWED_PUBLIC_KEYS"])["keys"][0]
        key_id = key["kid"]
        authentication_token = jwt.encode({"username": "x"}, "", headers={"kid": key_id})

        self.res({**event, "headers": {"authentication": authentication_token}})()
        load_user.assert_called_once_with(authentication_token)

    def test_unauthorized_when_jwt_header_lacks_kid(self):
        authentication_token = jwt.encode({"foo": "bar"}, "")
        resp = self.res({**event, "headers": {"authentication": authentication_token}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_unauthorized_when_no_matching_key_in_env_variable(self):
        authentication_token = jwt.encode({"kid": "foobar"}, "")
        resp = self.res({**event, "headers": {"authentication": authentication_token}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_unauthorized_when_jwt_header_malformed(self):
        resp = self.res({**event, "headers": {"authentication": "12345"}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_unauthorized_when_authentication_not_configured_correctly(self):
        with patch("lbz.resource.env", {}):
            resp = self.res({**event, "headers": {"authentication": "dummy"}})()
            assert resp.status_code == HTTPStatus.UNAUTHORIZED


ORIGIN_LOCALHOST = "http://localhost:3000"
ORIGIN_EXAMPLE = "https://api.example.com"


class TestCORSResource:
    def setup_class(self):
        environ["CORS_ORIGIN"] = f"{ORIGIN_LOCALHOST},{ORIGIN_EXAMPLE}"

    def teardown_class(self):
        del environ["CORS_ORIGIN"]

    def make_cors_handler(self, origins: List[str] = None, req_origin: str = None) -> CORSResource:
        an_event = defaultdict(MagicMock())
        an_event["headers"] = {"origin": req_origin} if req_origin is not None else {}
        cors_handler = CORSResource(an_event, ["GET", "POST"], origins=origins)
        return cors_handler

    @pytest.mark.parametrize(
        "req_origin, orig_outcome",
        [
            (None, ORIGIN_LOCALHOST),
            (ORIGIN_EXAMPLE, ORIGIN_EXAMPLE),
            ("invalid_origin", ORIGIN_LOCALHOST),
        ],
    )
    def test_cors_origin_headers_from_env_are_correct(self, req_origin, orig_outcome):
        headers = self.make_cors_handler(req_origin=req_origin).resp_headers_json[
            ALLOW_ORIGIN_HEADER
        ]
        assert headers == orig_outcome

    def test_cors_origin_headers_from_param_are_correct(self):
        origin_headers = [ORIGIN_LOCALHOST, ORIGIN_EXAMPLE]
        cors_handler = self.make_cors_handler(origins=origin_headers, req_origin=ORIGIN_EXAMPLE)
        assert cors_handler.resp_headers_json[ALLOW_ORIGIN_HEADER] == ORIGIN_EXAMPLE

    def test_cors_origin_headers_from_wildcard(self):
        cors_handler = self.make_cors_handler(
            origins=["https://*.lb.com"], req_origin="https://dev.test.lb.com"
        )
        assert cors_handler.resp_headers_json[ALLOW_ORIGIN_HEADER] == "https://dev.test.lb.com"

    def test_cors_origin_headers_from_wildcard_no_orgin(self):
        cors_handler = self.make_cors_handler(req_origin=None).resp_headers_json[
            ALLOW_ORIGIN_HEADER
        ]
        assert cors_handler == "http://localhost:3000"

    def test_cors_origin_headers_from_wildcard_star(self):
        assert self.make_cors_handler(origins=["*"]).resp_headers_json[ALLOW_ORIGIN_HEADER] == "*"
        cors_handler = self.make_cors_handler(origins=["*"], req_origin="http://localhost:3000")
        assert cors_handler.resp_headers_json[ALLOW_ORIGIN_HEADER] == "*"

    def test_all_headers(self):
        content_type = "image/jpeg"
        expected_header = "Content-Type, X-Amz-Date, Authentication, Authorization, X-Api-Key, X-Amz-Security-Token"  # noqa: E501

        assert self.make_cors_handler().resp_headers(content_type) == {
            "Access-Control-Allow-Headers": expected_header,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_LOCALHOST,
            "Content-Type": content_type,
        }

    def test_resp_headers_json(self):
        assert self.make_cors_handler().resp_headers_json["Content-Type"] == "application/json"

    def test_resp_headers_no_content_type_by_default(self):
        assert self.make_cors_handler().resp_headers().get("Content-Type") is None

    def test_options_request(self):
        inst = self.make_cors_handler(req_origin=ORIGIN_EXAMPLE)
        inst.method = "OPTIONS"
        assert inst().headers == {
            "Access-Control-Allow-Headers": ", ".join(
                CORSResource._cors_headers  # pylint: disable=protected-access
            ),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            ALLOW_ORIGIN_HEADER: ORIGIN_EXAMPLE,
        }

    @patch.object(CORSResource, "resp_headers", return_value={})
    def test_not_allow_oring_in_header(self, resp_headers_mock: MagicMock):
        an_event = defaultdict(MagicMock())
        an_event["method"] = "GET"
        an_event["headers"] = {"origin": "notlocalhost"}
        resp = CORSResource(an_event, ["GET", "POST"], origins="localhost")()
        assert resp.status_code >= 400
        resp_headers_mock.assert_called_once()


class TestPagination:
    @patch.object(PaginatedCORSResource, "__init__", return_value=None)
    def setup_method(self, _test_method, _init_mock: MagicMock) -> None:
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

    def test_get_pagination(self):
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

    def test_get_pagination_multifield_query_params(self):
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

    def test_no_prev_link_when_offset_minus_limit_lt_zero(self):
        links = self.resource.get_pagination(total_items=100, offset=10, limit=20)["links"]
        assert "prev" not in links

    def test_no_next_returned_when_offset_plus_limit_gt_total_items(self):
        links = self.resource.get_pagination(total_items=25, offset=20, limit=10)["links"]
        assert "next" not in links

    def test_pagination_uri_with_existing_pagination_query_params(self):
        self.resource.request.query_params = MultiDict({"offset": "3", "limit": "42"})
        expected = "/test/path?offset={offset}&limit={limit}"
        assert self.resource._pagination_uri == expected  # pylint: disable=protected-access

    def test_pagination_uri_without_query_params(self):
        self.resource.request.query_params = MultiDict({})
        expected = "/test/path?offset={offset}&limit={limit}"
        assert self.resource._pagination_uri == expected  # pylint: disable=protected-access
