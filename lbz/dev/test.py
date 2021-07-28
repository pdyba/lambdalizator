# coding=utf-8
"""Helper class for testing."""
from typing import Union

from lbz.dev.misc import Event
from lbz.misc import get_logger
from lbz.resource import Resource
from lbz.response import Response

logger = get_logger(__name__)


class Client:
    """
    Client created for testing purposes.
    """

    def __init__(self, resource: Resource):
        self.resource = resource

    def post(
        self,
        resource: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(resource, "POST", params, query_params, body, headers)

    def get(
        self,
        resource: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(resource, "GET", params, query_params, body, headers)

    def patch(
        self,
        resource: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(resource, "PATCH", params, query_params, body, headers)

    def put(
        self,
        resource: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(resource, "PUT", params, query_params, body, headers)

    def delete(
        self,
        resource: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(resource, "DELETE", params, query_params, body, headers)

    def _process(
        self,
        path: str,
        method: str,
        params: Union[dict, None],
        query_params: Union[dict, None],
        body: Union[dict, None],
        headers: Union[dict, None],
    ) -> Response:
        if query_params:
            for key, value in query_params.items():
                if not isinstance(value, list):
                    query_params[key] = [str(value)]
                else:
                    query_params[key] = [str(elem) for elem in value]
        return self.resource(
            Event(
                resource_path=path,
                method=method,
                body=body,
                path_params=params,
                query_params=query_params,
                headers=headers,
            )
        )()
