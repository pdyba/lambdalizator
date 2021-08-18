# coding=utf-8
"""
Dev misc tools.
"""
import json
import pathlib
from uuid import uuid4

from lbz.dev.event import EVENT_TEMPLATE

WORKING_DIR = pathlib.Path(__file__).parent.absolute()


class Event(dict):
    """Fake Event object for AWS Lambda compatibility"""

    def __init__(
        self,
        resource_path: str,
        method: str,
        body: dict = None,
        query_params: dict = None,
        path_params: dict = None,
        headers: dict = None,
    ) -> None:
        super().__init__(**json.loads(EVENT_TEMPLATE))

        self["resource"] = resource_path
        self["pathParameters"] = {} if path_params is None else path_params
        self["path"] = resource_path.format(**self.get("pathParameters", {}))
        self["method"] = method
        self["body"] = {} if body is None else body
        self["headers"] = {"Content-Type": "application/json"} if headers is None else headers
        self["queryStingParameters"] = query_params
        self["multiValueQueryStringParameters"] = query_params
        self["requestContext"]["resourcePath"] = self["resource"]
        self["requestContext"]["path"] = self["path"]
        self["requestContext"]["httpMethod"] = method
        self["requestContext"]["requestId"] = str(uuid4())

    def __repr__(self) -> str:
        return f"<Fake Event {self['method']} @ {self['path']} body: {self['body']}>"
