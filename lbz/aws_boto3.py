from functools import cached_property
from os import getenv
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_lambda import LambdaClient
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sns import SNSClient
    from mypy_boto3_sqs import SQSClient
    from mypy_boto3_ssm import SSMClient
else:
    CognitoIdentityProviderClient = object
    EventBridgeClient = object
    LambdaClient = object
    S3Client = object
    SNSClient = object
    SSMClient = object
    SQSClient = object
    DynamoDBClient = object


class Boto3Client:
    @cached_property
    def cognito_idp(self) -> CognitoIdentityProviderClient:
        return boto3.client("cognito-idp")

    @cached_property
    def dynamodb(self) -> DynamoDBClient:
        return boto3.client("dynamodb", endpoint_url=getenv("DYNAMODB_URL"))

    @cached_property
    def eventbridge(self) -> EventBridgeClient:
        return boto3.client("events")

    @cached_property
    def lambda_(self) -> LambdaClient:
        return boto3.client("lambda")

    @cached_property
    def s3(self) -> S3Client:
        return boto3.client("s3")

    @cached_property
    def sns(self) -> SNSClient:
        return boto3.client("sns")

    @cached_property
    def ssm(self) -> SSMClient:
        return boto3.client("ssm")

    @cached_property
    def sqs(self) -> SQSClient:
        return boto3.client("sqs")


client = Boto3Client()
