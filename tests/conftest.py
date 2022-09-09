# coding=utf-8
import os
from datetime import datetime, timedelta
from typing import Iterator, List, Type
from uuid import uuid4

import pytest
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.authz.authorizer import Authorizer
from lbz.authz.decorators import authorization
from lbz.collector import authz_collector
from lbz.dev.misc import APIGatewayEvent
from lbz.request import Request
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import Router, add_route
from tests import SAMPLE_PRIVATE_KEY
from tests.utils import encode_token


@pytest.fixture(scope="session")
def allowed_audiences() -> List[str]:
    return os.environ["ALLOWED_AUDIENCES"].split(",")


@pytest.fixture(autouse=True)
def clear_authz_collector() -> Iterator[None]:
    yield
    authz_collector.clean()


@pytest.fixture(autouse=True)
def clear_router_collector() -> Iterator[None]:
    yield
    Router().clear()


@pytest.fixture()
def sample_request() -> Request:
    # TODO: change to simple factory / parametrise it
    return Request(
        method="GET",
        body="",
        headers=CIMultiDict({"Content-Type": "application/json"}),
        user=None,
        uri_params={},
        context={},
        query_params=None,
        stage_vars={},
        is_base64_encoded=False,
    )


@pytest.fixture()
def sample_event() -> APIGatewayEvent:
    return APIGatewayEvent(
        resource_path="/",
        method="GET",
        headers={},
        path_params={},
        query_params={},
        body={},
    )


@pytest.fixture(scope="session", name="jwt_partial_payload")
def jwt_partial_payload_fixture() -> dict:
    return {
        "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "test-issuer",
        "aud": os.environ["ALLOWED_AUDIENCES"].split(",")[0],
    }


@pytest.fixture(scope="session", name="full_access_authz_payload")
def full_access_authz_payload_fixture(jwt_partial_payload: dict) -> dict:
    return {
        "allow": {"*": "*"},
        "deny": {},
        **jwt_partial_payload,
    }


@pytest.fixture(scope="session")
def full_access_auth_header(
    full_access_authz_payload: dict,
) -> str:
    return Authorizer.sign_authz(
        full_access_authz_payload,
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session")
def limited_access_auth_header(
    full_access_authz_payload: dict,
) -> str:
    return Authorizer.sign_authz(
        {
            **full_access_authz_payload,
            "allow": {"test_res": {"perm-name": {"allow": "*"}}},
            "deny": {},
        },
        SAMPLE_PRIVATE_KEY,
    )


@pytest.fixture(scope="session", name="username")
def username_fixture() -> str:
    return str(uuid4())


@pytest.fixture(scope="session", name="user_cognito")
def user_cognito_fixture(username: str, jwt_partial_payload: dict) -> dict:
    return {
        "cognito:username": username,
        "custom:id": str(uuid4()),
        "email": f"{str(uuid4())}@{str(uuid4())}.com",
        "custom:1": str(uuid4()),
        "custom:2": str(uuid4()),
        "custom:3": str(uuid4()),
        "custom:4": str(uuid4()),
        "custom:5": str(uuid4()),
        **jwt_partial_payload,
    }


@pytest.fixture(scope="session", name="user_token")
def user_token_fixture(user_cognito: dict) -> str:
    return encode_token(user_cognito)


@pytest.fixture(scope="session", name="user")
def user_fixture(user_token: str) -> User:
    return User(user_token)


@pytest.fixture()
def sample_request_with_user(user: User) -> Request:
    return Request(
        method="GET",
        body="",
        headers=CIMultiDict({"Content-Type": "application/json"}),
        context={},
        user=user,
        stage_vars={},
        is_base64_encoded=False,
        uri_params={},
    )


@pytest.fixture()
def sample_resource() -> Type[Resource]:
    """Be careful when doing any changes in this fixture"""

    class HelloWorld(Resource):
        @add_route("/", method="GET")
        def list(self) -> Response:
            return Response({"message": "HelloWorld"})

        @add_route("/t/{id}", method="GET")
        def get(self) -> Response:
            return Response({"message": "HelloWorld"})

    return HelloWorld


@pytest.fixture()
def sample_resource_with_authorization() -> Type[Resource]:
    """Be careful when doing any changes in this fixture - especially for Auth Collector"""

    class XResource(Resource):
        _name = "test_res"

        @add_route("/")
        @authorization("perm-name")
        def handler(self, restrictions: dict) -> Response:
            assert restrictions == {"allow": "*", "deny": None}
            return Response("x")

        @add_route("/garbage")
        @authorization()
        def garbage(self, restrictions: dict) -> Response:  # pylint: disable=unused-argument
            return Response("x")

    return XResource


@pytest.fixture()
def event_bridge_event() -> dict:
    return {
        "version": "0",
        "id": "1142f221-bf5a-ce51-0fa9-f36c149cc955",
        "detail-type": "TESTING",
        "source": "myapp",
        "account": "761598893945",
        "time": "2022-09-06T08:07:08Z",
        "region": "eu-central-1",
        "resources": [],
        "detail": {"yrdy": ["xxx", "xxx"]},
    }


@pytest.fixture()
def s3_event() -> dict:
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "eu-central-1",
                "eventTime": "2022-09-05T10:44:20.215Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {"principalId": "AWS:xxxxx:yyyyyy"},
                "requestParameters": {"sourceIPAddress": " 127.0.0.0"},
                "responseElements": {
                    "x-amz-request-id": "xxxxxxxx",
                    "x-amz-id-2": "aox+w/xxxxxx/yyyyyy",
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "eaa64161-9820-4527-a668-c330de1261e8",
                    "bucket": {
                        "name": "xxxxxxxxx",
                        "ownerIdentity": {"principalId": "xxxx"},
                        "arn": "arn:aws:s3:::xxxxxx",
                    },
                    "object": {
                        "key": "42.jpg",
                        "size": 72410,
                        "eTag": "b8cc43c508cfe98072a62c277c836a1d",
                        "sequencer": "006315D30415E18240",
                    },
                },
            }
        ]
    }


@pytest.fixture()
def sqs_event() -> dict:
    return {
        "Records": [
            {
                "messageId": "7b01c7a5-7fbc-471a-96de-162ecd7af944",
                "receiptHandle": "xxxxx",
                "body": '"test"',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1662374879945",
                    "SenderId": "xxxxxxx:yyyyy",
                    "ApproximateFirstReceiveTimestamp": "1662374879950",
                },
                "messageAttributes": {},
                "md5OfBody": "303b5c8988601647873b4ffd247d83cb",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:eu-central-1:xxxxxxxxx:queue-name",
                "awsRegion": "eu-central-1",
            }
        ]
    }


@pytest.fixture()
def api_gw_event() -> dict:
    return {
        "resource": "/testing",
        "path": "/testing",
        "httpMethod": "GET",
        "headers": {
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
            ),
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Host": "iba8xmzdjh.execute-api.eu-central-1.amazonaws.com",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "X-Amzn-Trace-Id": "Root=1-6315d48b-xxx",
            "X-Forwarded-For": " 127.0.0.0",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
        },
        "multiValueHeaders": {
            "accept": ["text/html,application/xhtml+xml,application/xml;q=0.9"],
            "accept-encoding": ["gzip, deflate, br"],
            "accept-language": ["en-GB,en-US;q=0.9,en;q=0.8"],
            "Host": ["xxxxxxx.execute-api.eu-central-1.amazonaws.com"],
            "sec-ch-ua": ['"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"'],
            "sec-ch-ua-mobile": ["?0"],
            "sec-ch-ua-platform": ['"macOS"'],
            "sec-fetch-dest": ["document"],
            "sec-fetch-mode": ["navigate"],
            "sec-fetch-site": ["cross-site"],
            "sec-fetch-user": ["?1"],
            "upgrade-insecure-requests": ["1"],
            "User-Agent": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"],
            "X-Amzn-Trace-Id": ["Root=1-6315d48b-50b207e84d165b1314658bef"],
            "X-Forwarded-For": ["127.0.0.0"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
        },
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "j5aovy",
            "resourcePath": "/testing",
            "httpMethod": "GET",
            "extendedRequestId": "X-xxxxxxxxx=",
            "requestTime": "05/Sep/2022:10:50:51 +0000",
            "path": "/default/testing",
            "accountId": "xxxxxxx",
            "protocol": "HTTP/1.1",
            "stage": "default",
            "domainPrefix": "xxxxx",
            "requestTimeEpoch": 1662375051195,
            "requestId": "61a92ae2-7bef-49d5-9ac3-24a255e67e4d",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "sourceIp": " 127.0.0.0",
                "principalOrgId": None,
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537",
                "user": None,
            },
            "domainName": "xxxxxxxx.execute-api.eu-central-1.amazonaws.com",
            "apiId": "xxxxxxxxx",
        },
        "body": None,
        "isBase64Encoded": False,
    }


@pytest.fixture()
def dirct_lambda_event() -> dict:
    return {"invoke_type": "direct_lambda_request", "op": "test-op", "data": {"data": 1}}


@pytest.fixture()
def dynamodb_event() -> dict:
    return {
        "Records": [
            {
                "eventID": "f0155a40c9d38fcc81dcfbd0e5c275xx",
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-central-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1662614599,
                    "Keys": {"id": {"S": "xxx-0fx7cb9e0x094f07994eeb3xbcb339d9"}},
                    "NewImage": {"key_string": {"S": "value_string"}},
                    "SequenceNumber": "0000000000000000",
                    "SizeBytes": 1780,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:eu-central-1:xxxxxxx:table/table-name/...",
            }
        ]
    }
