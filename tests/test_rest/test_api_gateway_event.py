from unittest.mock import ANY

from lbz.rest import APIGatewayEvent


class TestAPIGatewayEvent:
    def test_builds_basic_version_of_simulated_event(self) -> None:
        event = APIGatewayEvent("/", "GET")

        assert event == {
            "body": {},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "multiValueQueryStringParameters": {},
            "path": "/",
            "pathParameters": {},
            "requestContext": {
                "httpMethod": "GET",
                "path": "/",
                "requestId": ANY,
                "resourcePath": "/",
            },
            "resource": "/",
            "stageVariables": {},
            "isBase64Encoded": False,
        }

    def test_builds_event_based_on_data_declared_from_outside(self) -> None:
        event = APIGatewayEvent(
            resource_path="/<pid>",
            method="POST",
            body={"ala": "ma_aids"},
            query_params={"kod": 23},
            path_params={"pid": 123},
            headers={"Accept": "DarthJson"},
            is_base_64_encoded=True,
        )

        assert event == {
            "body": {"ala": "ma_aids"},
            "headers": {"Accept": "DarthJson"},
            "httpMethod": "POST",
            "isBase64Encoded": True,
            "multiValueQueryStringParameters": {"kod": ["23"]},
            "path": "/<pid>",
            "pathParameters": {"pid": 123},
            "requestContext": {
                "httpMethod": "POST",
                "path": "/<pid>",
                "requestId": ANY,
                "resourcePath": "/<pid>",
            },
            "resource": "/<pid>",
            "stageVariables": {},
        }
