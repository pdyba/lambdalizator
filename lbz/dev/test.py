"""Helper class for testing."""
from typing import Optional, Type

from lbz.resource import Resource
from lbz.response import Response
from lbz.rest import APIGatewayEvent


class Client:
    """
    Client created for testing purposes.
    """

    def __init__(self, resource: Type[Resource]):
        self.resource = resource

    def post(
        self,
        path: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(path, "POST", params, query_params, body, headers)

    def get(
        self,
        path: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(path, "GET", params, query_params, body, headers)

    def patch(
        self,
        path: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(path, "PATCH", params, query_params, body, headers)

    def put(
        self,
        path: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(path, "PUT", params, query_params, body, headers)

    def delete(
        self,
        path: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        return self._process(path, "DELETE", params, query_params, body, headers)

    def _process(
        self,
        path: str,
        method: str,
        params: Optional[dict],
        query_params: Optional[dict],
        body: Optional[dict],
        headers: Optional[dict],
    ) -> Response:
        return self.resource(
            APIGatewayEvent(
                resource_path=path,
                method=method,
                body=body,
                path_params=params,
                query_params=query_params,
                headers=headers,
            )
        )()
