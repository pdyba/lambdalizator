from collections.abc import Iterable


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


class LambdaSource:
    API_GW = "api_gw"
    DIRECT = "direct_lambda_request"
    DYNAMODB = "dynamodb"
    EVENT_BRIDGE = "event_bridge"
    S3 = "s3"
    SQS = "sqs"

    @classmethod
    def standard_aws_sources(cls) -> Iterable[str]:
        return cls.DYNAMODB, cls.S3, cls.SQS

    @classmethod
    def get_source(cls, event: dict) -> str:
        # FYI: AWS is very inconsistent in its way to provide the source information
        if event.get("httpMethod") is not None:
            return cls.API_GW
        if event.get("invoke_type") == cls.DIRECT:
            return cls.DIRECT
        if event.get("detail-type") is not None:
            return cls.EVENT_BRIDGE
        event = event["Records"][0] if event.get("Records") else event
        event_source: str = event.get("eventSource", "").replace("aws:", "")
        if event_source in cls.standard_aws_sources():
            return event_source
        raise NotImplementedError(f"Unsupported event type: {event_source}")

    @classmethod
    def is_from(cls, event: dict, expected_type: str) -> bool:
        return cls.get_source(event) == expected_type
