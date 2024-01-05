from __future__ import annotations

from lbz.dev.misc import APIGatewayEvent
from lbz.misc import get_logger
from lbz.resource import Resource
from lbz.response import Response

logger = get_logger(__name__)


class Client:
    """Client created for testing purposes."""

    def __init__(self, resource: type[Resource]):
        self.resource = resource

    def post(
        self,
        path: str,
        params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        return self._process(path, "POST", params, query_params, body, headers)

    def get(
        self,
        path: str,
        params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        return self._process(path, "GET", params, query_params, body, headers)

    def patch(
        self,
        path: str,
        params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        return self._process(path, "PATCH", params, query_params, body, headers)

    def put(
        self,
        path: str,
        params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        return self._process(path, "PUT", params, query_params, body, headers)

    def delete(
        self,
        path: str,
        params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        return self._process(path, "DELETE", params, query_params, body, headers)

    def _process(
        self,
        path: str,
        method: str,
        params: dict | None,
        query_params: dict | None,
        body: dict | None,
        headers: dict | None,
    ) -> Response:
        if query_params:
            for key, value in query_params.items():
                if not isinstance(value, list):
                    query_params[key] = [str(value)]
                else:
                    query_params[key] = [str(elem) for elem in value]
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
