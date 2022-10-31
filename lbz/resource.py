"""Resource Handler."""
from copy import deepcopy
from http import HTTPStatus
from typing import Callable, List, Optional, Union
from urllib.parse import urlencode

from multidict import CIMultiDict

from lbz._cfg import ALLOWED_PUBLIC_KEYS, CORS_HEADERS, CORS_ORIGIN
from lbz.authentication import User
from lbz.collector import authz_collector
from lbz.events.api import EventAPI
from lbz.exceptions import (
    LambdaFWException,
    NotFound,
    ServerError,
    Unauthorized,
    UnsupportedMethod,
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
        self.response: Response = None  # type: ignore

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
            self.response = endpoint(**self.path_params)
        except LambdaFWException as err:
            if 500 <= err.status_code < 600:
                logger.exception(err)
            else:
                logger.warning(err, exc_info=is_in_debug_mode())
            self.response = err.get_response(self.request.context["requestId"])
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(err)
            self.response = ServerError().get_response(self.request.context["requestId"])
        self._post_request_hook()
        return self.response

    def __repr__(self) -> str:
        return f"<Resource {self.method} @ {self.urn} >"

    def _get_user(self, headers: CIMultiDict) -> Union[None, User]:
        authentication = headers.get("Authentication")
        if authentication and ALLOWED_PUBLIC_KEYS.value:
            return User(authentication)
        if authentication:
            raise Unauthorized("Authentication method not supported")
        return None

    def _post_request_hook(self) -> None:
        """
        Makes the post_request_hook run-time friendly.
        """
        try:
            self.post_request_hook()
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(err)

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
        Place to configure default authorization.

        That will be used when Authorization Header is not in place.
        """
        return {}

    def get_authz_data(self) -> dict:
        return self._authz_collector.dump()


class CORSResource(Resource):
    """
    CORS capable resource.
    """

    _cors_headers = (
        "Content-Type",
        "X-Amz-Date",
        "Authentication",
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token",
    )

    def __init__(
        self,
        event: dict,
        methods: List[str],
        origins: List[str] = None,
        cors_headers: List[str] = None,
    ):
        # TODO: adjust the rest of the arguments in the near future too.
        super().__init__(event)
        cors_headers = cors_headers or CORS_HEADERS.value
        self._resp_headers = {
            ALLOW_ORIGIN_HEADER: self._get_allowed_origins(origins or CORS_ORIGIN.value),
            "Access-Control-Allow-Headers": ", ".join([*self._cors_headers, *cors_headers]),
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


class EventAwareResource(Resource):
    def __init__(self, event: dict):
        super().__init__(event)
        self.event_api = EventAPI()

    def post_request_hook(self) -> None:
        if self.response.is_ok():
            self.event_api.send()
        else:
            self.event_api.clear()
