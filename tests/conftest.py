#!/usr/local/bin/python3.8
# coding=utf-8
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
        # pylint issue #214
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
        # pylint issue #214
        path_params={},
        query_params={},
    )
