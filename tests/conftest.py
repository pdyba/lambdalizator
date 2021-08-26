# coding=utf-8
import pytest
from multidict import CIMultiDict

from lbz.dev.misc import Event
from lbz.request import Request

req = Request(
    body="",
    headers=CIMultiDict({"Content-Type": "application/json"}),
    uri_params={},
    method="GET",  # pylint issue #214
    query_params=None,
    context={},
    stage_vars={},
    is_base64_encoded=False,
    user=None,
)


@pytest.fixture(autouse=True)
def sample_request():
    return req


@pytest.fixture(autouse=True)
def sample_event():
    return Event(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body=req,
    )
