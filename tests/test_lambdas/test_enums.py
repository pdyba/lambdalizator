import pytest

from lbz.lambdas import LambdaSources

event_bridge_event = {
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

s3_event = {
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

sqs_event = {
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

api_gw_event = {
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

dirct_lambda_event = {"invoke_type": "direct_lambda_request", "op": "test-op", "data": {"data": 1}}

dynamodb_event = {
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


@pytest.mark.parametrize(
    "source_event, expected_type",
    [
        (dynamodb_event, LambdaSources.dynamodb),
        (s3_event, LambdaSources.s3),
        (sqs_event, LambdaSources.sqs),
        (api_gw_event, LambdaSources.api_gw),
        (event_bridge_event, LambdaSources.event_bridge),
        (dirct_lambda_event, LambdaSources.lambda_api),
    ],
)
def test_dynamo_db(source_event: dict, expected_type: str) -> None:
    assert LambdaSources.get_source(source_event) == expected_type
    assert LambdaSources.is_from(source_event, expected_type)
