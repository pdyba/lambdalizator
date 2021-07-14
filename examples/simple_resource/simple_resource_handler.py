# coding=utf-8
# pylint: disable=unused-argument, broad-except, no-member
"""
Simple Lambda Handler
"""
from lbz.exceptions import LambdaFWException

from simple_resource.simple_resource import HelloWorld


def handle(event, context):
    try:
        exp = HelloWorld(event)
        resp = exp()
        return resp
    except Exception:
        return LambdaFWException().to_dict()
