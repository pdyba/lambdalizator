from __future__ import annotations

import uuid

DEFAULT_HEADERS = {"Content-Type": "application/json"}


class APIGatewayEvent(dict):
    """Easy-to-use dictionary simulating the event coming from the API Gateway

    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    """

    def __init__(
        self,
        method: str,
        resource_path: str,
        path_params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
        is_base64_encoded: bool = False,
    ) -> None:
        super().__init__()

        self["resource"] = resource_path
        self["httpMethod"] = method
        self["pathParameters"] = {} if path_params is None else path_params
        self["path"] = resource_path.format(**self.get("pathParameters", {}))
        self["body"] = {} if body is None else body
        self["headers"] = DEFAULT_HEADERS if headers is None else headers
        self["multiValueQueryStringParameters"] = self._get_multi_value_query_params(query_params)
        self["requestContext"] = {
            "resourcePath": self["resource"],
            "path": self["path"],
            "httpMethod": method,
            "requestId": str(uuid.uuid4()),
        }
        self["stageVariables"] = {}
        self["isBase64Encoded"] = is_base64_encoded

    @staticmethod
    def _get_multi_value_query_params(query_params: dict | None) -> dict:
        multi_value_query_params: dict[str, list[str]] = {}
        if query_params:
            for key, value in query_params.items():
                if not isinstance(value, list):
                    multi_value_query_params[key] = [str(value)]
                else:
                    multi_value_query_params[key] = [str(elem) for elem in value]
        return multi_value_query_params
