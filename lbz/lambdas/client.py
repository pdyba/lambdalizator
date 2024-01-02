import json
from typing import Any, Iterable, Optional, Type, cast

from lbz.aws_boto3 import client
from lbz.dev import APIGatewayEvent
from lbz.lambdas.enums import LambdaResult, LambdaSource
from lbz.lambdas.exceptions import LambdaError
from lbz.lambdas.response import LambdaResponse
from lbz.misc import get_logger
from lbz.response import Response

logger = get_logger(__name__)


class SetsEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (set, frozenset)):
            return list(o)
        return json.JSONEncoder.default(self, o)


class LambdaClient:
    json_encoder: Type[json.JSONEncoder] = SetsEncoder

    @classmethod
    def invoke(
        cls,
        function_name: str,
        op: str,
        data: Optional[dict] = None,
        *,
        allowed_error_results: Iterable[str] = None,
        raise_if_error_resp: bool = False,
        asynchronous: bool = False,
    ) -> LambdaResponse:
        allowed_error_results = set(allowed_error_results or []) & set(LambdaResult.soft_errors())

        payload = {"invoke_type": LambdaSource.DIRECT, "op": op, "data": data}

        response = cast(LambdaResponse, cls._invoke(function_name, payload, asynchronous))

        lambda_result = response.get("result", LambdaResult.SERVER_ERROR)
        if lambda_result in LambdaResult.successes():
            return response
        if lambda_result in allowed_error_results:
            return response
        if raise_if_error_resp:
            raise LambdaError(function_name, op, lambda_result, response)

        # f-string used directly to keep messages unique from the monitoring/tracking perspective
        error_message = f"Error response from {function_name} Lambda (op: {op}): {lambda_result}"
        logger.error(error_message, extra=dict(data=data, response=response))
        return response

    @classmethod
    def request(
        cls,
        function_name: str,
        method: str,
        path: str,
        path_params: Optional[dict] = None,
        query_params: Optional[dict] = None,
        body: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Response:
        payload = APIGatewayEvent(
            resource_path=path,
            method=method,
            path_params=params,
            query_params=query_params,
            body=body,
            headers=headers,
        )

        response = cls._invoke(function_name, payload)

        return Response(
            response["body"],
            headers=response.get("headers", {}),
            status_code=response["statusCode"],
            base64_encoded=response.get("isBase64Encoded", False),
        )

    @classmethod
    def _invoke(cls, function_name: str, payload: dict, asynchronous: bool = False) -> dict:
        raw_response = client.lambda_.invoke(
            FunctionName=function_name,
            Payload=json.dumps(payload, cls=cls.json_encoder).encode("utf-8"),
            InvocationType="Event" if asynchronous else "RequestResponse",
        )
        if asynchronous:
            # Lambda invoked asynchronously only includes a status code in the response
            return {"result": LambdaResult.ACCEPTED}

        try:
            response: dict = json.loads(raw_response["Payload"].read().decode("utf-8"))
            return response
        except Exception:
            message = "Invalid response received from %s Lambda (op: %s)"
            logger.error(
                message,
                function_name,
                payload.get("op", payload.get("path")),
                extra=dict(data=payload, response=raw_response),
            )
            raise
