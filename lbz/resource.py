#!/usr/local/bin/python3.8
# coding=utf-8
"""
Resource Handler.
"""
from os import environ
import traceback

from jose import jwt
from lbz.exceptions import ValidationError

from lbz.authz import Authorizer
from lbz.communication import Request
from lbz.exceptions import (
    BadRequestError,
    LambdaFWException,
    WrongURI,
    UnsupportedMethod,
)
from lbz.misc import get_logger
from lbz.router import Router

logger = get_logger(__name__)

PRINT_TRACEBACK = environ.get("PRINT_TRACEBACK", "0")


class Resource:
    _name = ""
    _router = Router()
    _authorizer = Authorizer()

    def __init__(self, event):
        self.path = event.get("requestContext", {}).get("resourcePath")
        self.uids = (
            event.get("pathParameters")
            if event.get("pathParameters") is not None
            else {}
        )
        self.method = event["requestContext"]["httpMethod"]
        headers = event["headers"]
        # We don't need to authenticate - this will be done by Cognito
        # Cognito should be parsed later on to something nicer ;)
        authentication = headers.get("Authentication", headers.get("authentication"))
        self.request = Request(
            headers=headers,
            uri_params=self.uids,
            method=self.method,
            body=event["body"],
            context=event["requestContext"],
            stage_vars=event["stageVariables"],
            is_base64_encoded=event.get("isBase64Encoded", False),
            query_params=event["multiValueQueryStringParameters"],
            user=jwt.get_unverified_claims(authentication) if authentication else None,
        )
        if authorization := headers.get("Authorization", headers.get("authorization")):
            self._authorizer.set_policy(authorization)
        else:
            self._authorizer.set_policy(self.get_guest_authorization())

    def __call__(self):
        try:
            if self.path is None or self.path not in self._router:
                logger.error(
                    "Couldn't find PATH %s in current paths %s", self.path, self._router
                )
                raise WrongURI()
            if self.method not in self._router[self.path]:
                raise UnsupportedMethod(method=self.method)
            try:  # Map marshmallow's validation error to LambdaFWException
                return getattr(self, self._router[self.path][self.method])(**self.uids)
            except ValidationError as e:
                raise BadRequestError(e.messages)
        except LambdaFWException as e:
            logger.format_error(e)
            if bool(PRINT_TRACEBACK) and 500 <= e.status_code < 600:
                e.message = traceback.format_exc()
            return e.get_resp()

    def __repr__(self):
        return f"<Resource {self.method} @ {self.path} UIDS: {self.uids}>"

    def get_guest_authorization(self):
        """
        It should be overwritten after inheritance with a method to obtain guest auth.
        """
        logger.error("Using default guest authorization which gives Admin.")
        return self._authorizer.sign_authz({"allow": {"*": "*"}, "deny": {}})
