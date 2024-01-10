import uuid
from unittest.mock import ANY, MagicMock, patch

from lbz.rest import APIGatewayEvent


class TestAPIGatewayEvent:
    @patch.object(uuid, "uuid4")
    def test_builds_basic_version_of_simulated_event(self, mocked_uuid4: MagicMock) -> None:
        mocked_uuid4.return_value = "<mocked-uuid-value>"

        event = APIGatewayEvent(
            method="GET",
            resource_path="/",
        )

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
                "requestId": "<mocked-uuid-value>",
                "resourcePath": "/",
            },
            "resource": "/",
            "stageVariables": {},
            "isBase64Encoded": False,
        }

    def test_builds_event_based_on_data_declared_from_outside(self) -> None:
        event = APIGatewayEvent(
            method="POST",
            resource_path="/{pid}",
            path_params={"pid": 123},
            query_params={
                "kot": 23,
                "ma": "duze",
                "aids": ["lol", "xd"],
            },
            body={"ala": "ma_aids"},
            headers={"Accept": "DarthJson"},
            is_base64_encoded=True,
        )

        assert event == {
            "body": {"ala": "ma_aids"},
            "headers": {"Accept": "DarthJson"},
            "httpMethod": "POST",
            "isBase64Encoded": True,
            "multiValueQueryStringParameters": {
                "aids": ["lol", "xd"],
                "kot": ["23"],
                "ma": ["duze"],
            },
            "path": "/123",
            "pathParameters": {"pid": 123},
            "requestContext": {
                "httpMethod": "POST",
                "path": "/123",
                "requestId": ANY,
                "resourcePath": "/{pid}",
            },
            "resource": "/{pid}",
            "stageVariables": {},
        }
