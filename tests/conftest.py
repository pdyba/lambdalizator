#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access, too-few-public-methods
import pytest
from multidict import CIMultiDict

from lbz.dev.misc import Event
from lbz.request import Request


@pytest.fixture
def sample_request():
    return Request(
        headers=CIMultiDict({"Content-Type": "application/json"}),
        uri_params={},
        method="GET",
        body="",
        context={},
        stage_vars={},
        is_base64_encoded=False,
        query_params=None,
        user=None,
    )


@pytest.fixture
def sample_event():
    return Event(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
    )
