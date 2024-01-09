import uuid
from unittest.mock import ANY, MagicMock, patch

import pytest

from lbz.rest import APIGatewayEvent


class TestAPIGatewayEvent:
    @patch.object(uuid, "uuid4")
    @pytest.mark.parametrize("uuid4", ["uuid-1", "uuid-2", "uuid-3"])
    def test_builds_basic_version_of_simulated_event(
        self, mocked_uuid4: MagicMock, uuid4: str
    ) -> None:
        mocked_uuid4.return_value = uuid4
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
                "requestId": uuid4,
                "resourcePath": "/",
            },
            "resource": "/",
            "stageVariables": {},
            "isBase64Encoded": False,
        }

    def test_builds_event_based_on_data_declared_from_outside(self) -> None:
        event = APIGatewayEvent(
            resource_path="/{pid}",
            method="POST",
            body={"ala": "ma_aids"},
            query_params={"kod": 23},
            path_params={"pid": 123},
            headers={"Accept": "DarthJson"},
            is_base64_encoded=True,
        )

        assert event == {
            "body": {"ala": "ma_aids"},
            "headers": {"Accept": "DarthJson"},
            "httpMethod": "POST",
            "isBase64Encoded": True,
            "multiValueQueryStringParameters": {"kod": ["23"]},
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

    def test_building_of_multivalue_query_params(self) -> None:
        event = APIGatewayEvent(
            method="GET",
            resource_path="/",
            query_params={"kot": 23, "ma": "duze", "aids": ["lol", "xd"]},
        )

        assert event == {
            "body": {},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "multiValueQueryStringParameters": {
                "aids": ["lol", "xd"],
                "kot": ["23"],
                "ma": ["duze"],
            },
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
