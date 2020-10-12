#!/usr/local/bin/python3.8
# coding=utf-8
"""
Resource Handler.
"""
import json
import traceback

from os import environ
from typing import Union

from lbz.authentication import get_matching_jwk, User
from lbz.authz import Authorizer
from lbz.request import Request
from lbz.exceptions import (
    LambdaFWException,
    WrongURI,
    Unauthorized,
    UnsupportedMethod,
    ServerError
)
from lbz.misc import get_logger
from lbz.router import Router

logger = get_logger(__name__)


class Resource:
    _name = ""
    _router = Router()
    _authorizer = Authorizer()

    def __init__(self, event):
        self._load_configuration()
        self.path = event.get("requestContext", {}).get("resourcePath")
        self.uids = event.get("pathParameters") if event.get("pathParameters") is not None else {}
        self.method = event["requestContext"]["httpMethod"]
        headers = event["headers"]
        self.request = Request(
            headers=headers,
            uri_params=self.uids,
            method=self.method,
            body=event["body"],
            context=event["requestContext"],
            stage_vars=event["stageVariables"],
            is_base64_encoded=event.get("isBase64Encoded", False),
            query_params=event["multiValueQueryStringParameters"],
            user=self._get_user(headers),
        )
        if authorization := headers.get("Authorization", headers.get("authorization")):
            self._authorizer.set_policy(authorization)
        else:
            self._authorizer.set_policy(self.get_guest_authorization())

    def __call__(self):
        try:
            if self.path is None or self.path not in self._router:
                logger.error("Couldn't find PATH %s in current paths %s", self.path, self._router)
                raise WrongURI()
            if self.method not in self._router[self.path]:
                raise UnsupportedMethod(method=self.method)
            return getattr(self, self._router[self.path][self.method])(**self.uids)
        except LambdaFWException as e:
            logger.format_error(e)
            if self.print_traceback and 500 <= e.status_code < 600:
                e.message = traceback.format_exc()
            return e.get_resp()

    def __repr__(self):
        return f"<Resource {self.method} @ {self.path} UIDS: {self.uids}>"

    def _load_configuration(self):
        self.print_traceback = bool(int(environ.get("PRINT_TRACEBACK", "0")))
        self.use_cognito_auth = bool(int(environ.get("COGNITO_AUTHENTICATION", "0")))
        if self.use_cognito_auth:
            try:
                self.cognito_public_keys = json.loads(environ["COGNITO_PUBLIC_KEYS"])["keys"]
                self.cognito_allowed_clients = environ["COGNITO_ALLOWED_CLIENTS"].split()
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                logger.error(f"Invalid cognito configuration, details: \n{str(e)}")
                raise ServerError

    def _get_user(self, headers: dict) -> Union[None, User]:
        authentication = headers.get("Authentication", headers.get("authentication"))
        if authentication and self.use_cognito_auth:
            pub_key = get_matching_jwk(authentication, self.cognito_public_keys)
            return User(authentication, pub_key, self.cognito_allowed_clients)
        elif authentication:
            logger.error(f"Authentication method not supported, token: {authentication}")
            raise Unauthorized
        return None

    def get_guest_authorization(self):
        """
        It should be overwritten after inheritance with a method to obtain guest auth.
        """
        logger.error("Using default guest authorization which gives Admin.")
        return self._authorizer.sign_authz({"allow": {"*": "*"}, "deny": {}})
