# coding=utf-8
"""
Simple Lambda Handler
"""
from lbz.exceptions import LambdaFWException

from .simple_resource import HelloWorld


def handle(event, context):
    try:
        exp = HelloWorld(event)
        resp = exp()
        return resp
    except Exception:  # pylint: disable=broad-except
        return LambdaFWException().get_response(
            context.aws_request_id
        )  # pylint: disable=no-member
