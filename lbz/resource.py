# coding=utf-8
"""Resource Handler."""
from copy import deepcopy
from http import HTTPStatus
from os import environ as env
from typing import Union, List, Optional, Callable
from urllib.parse import urlencode

from multidict import CIMultiDict

from lbz.authentication import User
from lbz.collector import authz_collector
from lbz.exceptions import (
    LambdaFWException,
    NotFound,
    Unauthorized,
    UnsupportedMethod,
    ServerError,
)
from lbz.misc import get_logger, is_in_debug_mode
from lbz.request import Request
from lbz.response import Response
from lbz.router import Router


ALLOW_ORIGIN_HEADER = "Access-Control-Allow-Origin"

logger = get_logger(__name__)


class Resource:
    """
    Resource class.
    """

    _name: str = ""
    _router = Router()
    _authz_collector = authz_collector

    @classmethod
    def get_name(cls) -> str:
        return cls._name or cls.__name__.lower()

    def __init__(self, event: dict):
        self._load_configuration()
        self.urn = event["path"]  # TODO: Variables should match corresponding event fields
        self.path = event.get("requestContext", {}).get("resourcePath")
        self.path_params = event.get("pathParameters") or {}  # DO NOT refactor
        self.method = event["requestContext"]["httpMethod"]
        headers = CIMultiDict(event.get("headers", {}))
        self.request = Request(
            headers=headers,
            uri_params=self.path_params,
            method=self.method,
            body=event["body"],
            context=event["requestContext"],
            stage_vars=event["stageVariables"],
            is_base64_encoded=event.get("isBase64Encoded", False),
            query_params=event["multiValueQueryStringParameters"],
        )
        self._authz_collector.set_resource(self.get_name())
        self._authz_collector.set_guest_permissions(self.get_guest_authorization())

    def __call__(self) -> Response:
        try:
            self.pre_request_hook()

            if self.path is None or self.path not in self._router:
                logger.warning("Couldn't find %s in current paths: %s", self.path, self._router)
                raise NotFound
            if self.method not in self._router[self.path]:
                raise UnsupportedMethod(method=self.method)
            self.request.user = self._get_user(self.request.headers)
            endpoint: Callable = getattr(self, self._router[self.path][self.method])
            response: Response = endpoint(**self.path_params)
            return response
        except LambdaFWException as err:
            if 500 <= err.status_code < 600:
                logger.exception(err)
            else:
                logger.warning(err, exc_info=is_in_debug_mode())
            return err.get_response(self.request.context["requestId"])
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(err)
            return ServerError().get_response(self.request.context["requestId"])
        finally:
            self.post_request_hook()

    def __repr__(self) -> str:
        return f"<Resource {self.method} @ {self.urn} >"

    def _load_configuration(self) -> None:
        self.auth_enabled = env.get("ALLOWED_PUBLIC_KEYS") or env.get("ALLOWED_AUDIENCES")

    def _get_user(self, headers: CIMultiDict) -> Union[None, User]:
        authentication = headers.get("Authentication")
        if authentication and self.auth_enabled:
            return User(authentication)
        if authentication:
            raise Unauthorized("Authentication method not supported")
        return None

    def pre_request_hook(self) -> None:
        """
        Place to configure pre request hooks.
        """

    def post_request_hook(self) -> None:
        """
        Place to configure post request hooks.
        """

    @staticmethod
    def get_guest_authorization() -> dict:
        """
        Place to configure default authorization. That will be used when Authorization Header is not in place.
        """
        return {}

    def get_authz_data(self) -> dict:
        return self._authz_collector.dump()


class CORSResource(Resource):
    """
    CORS capable resource.
    """

    _cors_headers = [
        "Content-Type",
        "X-Amz-Date",
        "Authentication",
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token",
    ]

    def __init__(self, event: dict, methods: List[str], origins: List[str] = None):
        super().__init__(event)

        self._resp_headers = {
            ALLOW_ORIGIN_HEADER: self._get_allowed_origins(
                origins or env.get("CORS_ORIGIN", "").split(",")
            ),
            "Access-Control-Allow-Headers": ", ".join(self._cors_headers),
            "Access-Control-Allow-Methods": ", ".join([*methods, "OPTIONS"]),
        }

    def __call__(self) -> Response:
        if self.method == "OPTIONS":
            return Response("", headers=self.resp_headers(), status_code=HTTPStatus.NO_CONTENT)

        resp = super().__call__()
        if resp.status_code >= 400 and ALLOW_ORIGIN_HEADER not in resp.headers:
            resp.headers.update(self.resp_headers())
        return resp

    def _get_allowed_origins(self, origins: List[str]) -> str:
        """
        Checks requests origins against allowed origins.
        """
        if "*" in origins:
            return "*"
        request_origin: Optional[str] = self.request.headers.get("Origin")
        if request_origin:
            for allowed_origin in origins:
                if request_origin == allowed_origin:
                    return request_origin
                if "*" in allowed_origin:
                    service, domain = allowed_origin.split("*")
                    if request_origin.startswith(service) and request_origin.endswith(domain):
                        return request_origin
        return origins[0]

    def resp_headers(self, content_type: str = "") -> dict:
        """
        Properly formatted headers.
        """
        return (
            {**self._resp_headers, "Content-Type": content_type}
            if content_type
            else deepcopy(self._resp_headers)
        )

    @property
    def resp_headers_json(self) -> dict:
        """
        Properly formatted json headers.
        """
        return self.resp_headers(content_type="application/json")


class PaginatedCORSResource(CORSResource):
    """
    Resource for standardised pagination.
    """

    def get_pagination(self, total_items: int, limit: int, offset: int) -> dict:
        """
        Responsible for paginating the requests.
        """
        base_link = self._pagination_uri
        links = {
            "current": base_link.format(offset=offset, limit=limit),
            "last": base_link.format(offset=max(total_items - limit, 0), limit=limit),
        }
        if previous_offset := max(offset - limit, 0):
            links["prev"] = base_link.format(offset=previous_offset, limit=limit)
        next_offset = offset + limit if offset + limit < total_items else None
        if next_offset:
            links["next"] = base_link.format(offset=next_offset, limit=limit)
        return {
            "count": total_items,
            "links": links,
        }

    @property
    def _pagination_uri(self) -> str:
        if query_params := self.request.query_params.original_items(
            keys_to_skip=["offset", "limit"]
        ):
            encoded_params = urlencode(query_params, doseq=True)  # type: ignore
            return f"{self.urn}?{encoded_params}&offset={{offset}}&limit={{limit}}"
        return f"{self.urn}?offset={{offset}}&limit={{limit}}"
