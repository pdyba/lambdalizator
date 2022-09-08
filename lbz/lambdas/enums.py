from typing import Iterable, cast

from lbz.consts import DIRECT_LAMBDA_REQUEST


class LambdaResult:
    ACCEPTED = "ACCEPTED"
    OK = "OK"
    MULTI_STATUS = "MULTI_STATUS"
    # soft errors
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    # hard errors
    CONTRACT_ERROR = "CONTRACT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"

    @classmethod
    def successes(cls) -> Iterable[str]:
        return cls.ACCEPTED, cls.OK, cls.MULTI_STATUS

    @classmethod
    def soft_errors(cls) -> Iterable[str]:
        """Strongly client-dependent errors - in most cases they should be passed on"""
        return cls.BAD_REQUEST, cls.NOT_FOUND, cls.UNAUTHORIZED

    @classmethod
    def hard_errors(cls) -> Iterable[str]:
        """Critical errors affecting communication - except in rare cases, they should be raised"""
        return cls.CONTRACT_ERROR, cls.SERVER_ERROR


class LambdaSources:
    dynamodb = "dynamodb"
    s3 = "s3"
    sqs = "sqs"
    api_gw = "api_gw"
    event_bridge = "event_bridge"
    lambda_api = DIRECT_LAMBDA_REQUEST

    @classmethod
    def standard_aws_events(cls) -> Iterable:
        return cls.dynamodb, cls.s3, cls.sqs

    @staticmethod
    def is_from_lambda_api(event: dict) -> bool:
        return event.get("invoke_type") == DIRECT_LAMBDA_REQUEST

    @staticmethod
    def is_from_api_gateway(event: dict) -> bool:
        return event.get("httpMethod") is not None

    @staticmethod
    def is_from_event_bridge(event: dict) -> bool:
        return event.get("detail-type") is not None

    @classmethod
    def get_source(cls, event: dict) -> str:
        if cls.is_from_api_gateway(event):
            return cls.api_gw
        if cls.is_from_lambda_api(event):
            return cls.lambda_api
        if cls.is_from_event_bridge(event):
            return cls.event_bridge
        if event.get("Records"):
            event = event["Records"][0]
        if (evt := event.get("eventSource", "").replace("aws:", "")) in cls.standard_aws_events():
            return cast(str, evt)
        raise NotImplementedError("Unsupported event type")

    @classmethod
    def is_from(cls, event: dict, expected_type: str) -> bool:
        return cls.get_source(event) == expected_type
