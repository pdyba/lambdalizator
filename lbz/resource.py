#!/usr/local/bin/python3.8
# coding=utf-8
"""Resource Handler."""
import traceback
from os import environ as env
from typing import Union

from multidict import CIMultiDict

from lbz.authentication import User
from lbz.exceptions import LambdaFWException, NotFound, Unauthorized, UnsupportedMethod
from lbz.misc import get_logger
from lbz.request import Request
from lbz.response import Response
from lbz.router import Router

logger = get_logger(__name__)


class Resource:
    _name = ""
    _router = Router()

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

    def __call__(self) -> Response:
        try:
            if self.path is None or self.path not in self._router:
                logger.error("Couldn't find %s in current paths: %s", self.path, self._router)
                raise NotFound
            if self.method not in self._router[self.path]:
                raise UnsupportedMethod(method=self.method)
            self.request.user = self._get_user(self.request.headers)
            return getattr(self, self._router[self.path][self.method])(**self.path_params)
        except LambdaFWException as e:
            logger.format_error(e)
            if self.print_traceback and 500 <= e.status_code < 600:
                e.message = traceback.format_exc()
            return e.get_response(self.request.context["requestId"])

    def __repr__(self):
        return f"<Resource {self.method} @ {self.urn} >"

    def _load_configuration(self) -> None:
        self.print_traceback = bool(int(env.get("PRINT_TRACEBACK", "0")))
        self.auth_enabled = env.get("ALLOWED_PUBLIC_KEYS") or env.get("ALLOWED_AUDIENCES")

    def _get_user(self, headers: CIMultiDict) -> Union[None, User]:
        authentication = headers.get("Authentication")
        if authentication and self.auth_enabled:
            return User(authentication)
        elif authentication:
            logger.error(f"Authentication method not supported, token: {authentication}")
            raise Unauthorized
        return None
