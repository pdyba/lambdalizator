# coding=utf-8
# pylint: disable=unused-argument,broad-except, no-member, no-name-in-module
"""
Simple Lambda Handler
"""
from lbz.exceptions import LambdaFWException

from simple_resource.simple_resource import HelloWorldWithAuthorization


def handle(event, context):
    try:
        exp = HelloWorldWithAuthorization(event)
        resp = exp()
        return resp
    except Exception:
        return LambdaFWException().to_dict()
