from typing import Any


class LambdaClientContextMobileClient:
    installation_id: str
    app_title: str
    app_version_name: str
    app_version_code: str
    app_package_name: str


class LambdaClientContext:
    client: LambdaClientContextMobileClient
    custom: dict[str, Any]
    env: dict[str, Any]


class LambdaCognitoIdentity:
    cognito_identity_id: str
    cognito_identity_pool_id: str


class LambdaContext:  # TODO: Replace with typing.Protocol to avoid using this class in production
    """https://docs.aws.amazon.com/lambda/latest/dg/python-context.html"""

    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: LambdaCognitoIdentity
    client_context: LambdaClientContext

    def get_remaining_time_in_millis(self) -> int:
        raise NotImplementedError()
