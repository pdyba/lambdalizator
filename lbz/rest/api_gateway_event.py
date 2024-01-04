from typing import Optional
from uuid import uuid4

DEFAULT_HEADERS = {"Content-Type": "application/json"}


class APIGatewayEvent(dict):
    """Easy-to-use dictionary simulating the event coming from the API Gateway"""

    def __init__(
        self,
        resource_path: str,
        method: str,
        body: Optional[dict] = None,
        query_params: Optional[dict] = None,
        path_params: Optional[dict] = None,
        headers: Optional[dict] = None,
        is_base_64_encoded: bool = False,
    ) -> None:
        super().__init__()

        self["resource"] = resource_path
        self["httpMethod"] = method
        self["pathParameters"] = {} if path_params is None else path_params
        self["path"] = resource_path.format(**self.get("pathParameters", {}))
        self["body"] = {} if body is None else body
        self["headers"] = DEFAULT_HEADERS if headers is None else headers
        self["multiValueQueryStringParameters"] = self._extract_query_params(query_params)
        self["requestContext"] = {
            "resourcePath": self["resource"],
            "path": self["path"],
            "httpMethod": method,
            "requestId": str(uuid4()),
        }
        self["stageVariables"] = {}
        self["isBase64Encoded"] = is_base_64_encoded

    @staticmethod
    def _extract_query_params(query_params: Optional[dict]) -> dict:
        extracted_query_aparams = {}
        if query_params:

            for key, value in query_params.items():
                if not isinstance(value, list):
                    extracted_query_aparams[key] = [str(value)]
                else:
                    extracted_query_aparams[key] = [str(elem) for elem in value]
        return extracted_query_aparams
