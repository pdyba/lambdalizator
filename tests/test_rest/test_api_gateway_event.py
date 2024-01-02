from unittest.mock import ANY

from lbz.rest import APIGatewayEvent


class TestAPIGatewayEvent:
    def test_structure_is_as_expected_when_no_body(self) -> None:
        event = APIGatewayEvent("/", "GET")

        assert event == {
            "body": {},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "method": "GET",
            "multiValueQueryStringParameters": None,
            "path": "/",
            "pathParameters": {},
            "queryStringParameters": None,
            "requestContext": {
                "httpMethod": "GET",
                "path": "/",
                "requestId": ANY,
                "resourcePath": "/",
            },
            "resource": "/",
            "stageVariables": {},
        }

    def test_structure_is_as_expected_with_body(self) -> None:
        event = APIGatewayEvent("/body", "POST", {"ala": "ma_aids"})

        assert event == {
            "body": {"ala": "ma_aids"},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "POST",
            "method": "POST",
            "multiValueQueryStringParameters": None,
            "path": "/body",
            "pathParameters": {},
            "queryStringParameters": None,
            "requestContext": {
                "httpMethod": "POST",
                "path": "/body",
                "requestId": ANY,
                "resourcePath": "/body",
            },
            "resource": "/body",
            "stageVariables": {},
        }

    def test_structure_is_as_expected_with_query_params(self) -> None:
        event = APIGatewayEvent("/qp", "GET", query_params={"kod": 23})

        assert event == {
            "body": {},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "method": "GET",
            "multiValueQueryStringParameters": {"kod": ["23"]},
            "path": "/qp",
            "pathParameters": {},
            "queryStringParameters": {"kod": ["23"]},
            "requestContext": {
                "httpMethod": "GET",
                "path": "/qp",
                "requestId": ANY,
                "resourcePath": "/qp",
            },
            "resource": "/qp",
            "stageVariables": {},
        }

    def test_structure_is_as_expected_with_path_parmas(self) -> None:
        event = APIGatewayEvent("/{pid}", "GET", path_params={"pid": 123})

        assert event == {
            "body": {},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "method": "GET",
            "multiValueQueryStringParameters": None,
            "path": "/123",
            "pathParameters": {"pid": 123},
            "queryStringParameters": None,
            "requestContext": {
                "httpMethod": "GET",
                "path": "/123",
                "requestId": ANY,
                "resourcePath": "/{pid}",
            },
            "resource": "/{pid}",
            "stageVariables": {},
        }

    def test_structure_is_as_expected_with_headers(self) -> None:
        event = APIGatewayEvent("/", "GET", headers={"Accept": "DarthJson"})

        assert event == {
            "body": {},
            "headers": {"Accept": "DarthJson"},
            "httpMethod": "GET",
            "method": "GET",
            "multiValueQueryStringParameters": None,
            "path": "/",
            "pathParameters": {},
            "queryStringParameters": None,
            "requestContext": {
                "httpMethod": "GET",
                "path": "/",
                "requestId": ANY,
                "resourcePath": "/",
            },
            "resource": "/",
            "stageVariables": {},
        }

    def test_structure_is_as_expected_with_base64(self) -> None:
        event = APIGatewayEvent("/", "GET", is_base_64_encoded=True)

        assert event == {
            "body": {},
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "method": "GET",
            "multiValueQueryStringParameters": None,
            "path": "/",
            "pathParameters": {},
            "queryStringParameters": None,
            "requestContext": {
                "httpMethod": "GET",
                "path": "/",
                "requestId": ANY,
                "resourcePath": "/",
            },
            "resource": "/",
            "stageVariables": {},
            "isBase64Encoded": True,
        }
