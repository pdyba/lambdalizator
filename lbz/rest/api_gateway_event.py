from uuid import uuid4

DEFAULT_HEADERS = {"Content-Type": "application/json"}


class APIGatewayEvent(dict):
    """Easy-to-use dictionary simulating the event coming from the API Gateway"""

    def __init__(
        self,
        resource_path: str,
        method: str,
        body: dict = None,
        query_params: dict = None,
        path_params: dict = None,
        headers: dict = None,
    ) -> None:
        super().__init__()

        if query_params:
            for key, value in query_params.items():
                if not isinstance(value, list):
                    query_params[key] = [str(value)]
                else:
                    query_params[key] = [str(elem) for elem in value]

        self["resource"] = resource_path
        self["pathParameters"] = {} if path_params is None else path_params
        self["path"] = resource_path.format(**self.get("pathParameters", {}))
        self["method"] = method
        self["body"] = {} if body is None else body
        self["headers"] = DEFAULT_HEADER if headers is None else headers
        self["queryStingParameters"] = query_params
        self["multiValueQueryStringParameters"] = query_params
        self["requestContext"] = {
            "resourcePath": self["resource"],
            "path": self["path"],
            "httpMethod": method,
            "requestId": str(uuid4()),
        }
        self["stageVariables"] = None

    def __repr__(self) -> str:
        return f"<API Gateway Event {self['method']} @ {self['path']} body: {self['body']}>"
