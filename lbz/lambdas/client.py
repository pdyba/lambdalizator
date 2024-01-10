from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, cast

from lbz.aws_boto3 import client
from lbz.lambdas.enums import LambdaResult, LambdaSource
from lbz.lambdas.exceptions import LambdaError
from lbz.lambdas.response import LambdaResponse
from lbz.misc import get_logger
from lbz.response import Response
from lbz.rest import APIGatewayEvent

logger = get_logger(__name__)


class SetsEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (set, frozenset)):
            return list(o)
        return json.JSONEncoder.default(self, o)


class LambdaClient:
    json_encoder: type[json.JSONEncoder] = SetsEncoder

    @classmethod
    def invoke(
        cls,
        function_name: str,
        op: str,
        data: dict | None = None,
        *,
        allowed_error_results: Iterable[str] | None = None,
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

        # f-string used directly to keep messages unique from a monitoring/tracking perspective
        error_message = f"Error response from {function_name} Lambda (op: {op}): {lambda_result}"
        logger.error(error_message, extra={"data": data, "response": response})
        return response

    @classmethod
    def request(
        cls,
        function_name: str,
        method: str,
        path: str,
        path_params: dict | None = None,
        query_params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        # TODO: consider raising an error if response >= 400
        event = APIGatewayEvent(
            method=method,
            resource_path=path,
            path_params=path_params,
            query_params=query_params,
            body=body,
            headers=headers,
        )

        response = cls._invoke(function_name, payload=event)

        return Response(
            response["body"],
            headers=response["headers"],
            status_code=response["statusCode"],
            base64_encoded=response["isBase64Encoded"],
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
            # f-string used directly to keep messages unique from a monitoring/tracking perspective
            error_message = f"Invalid response received from {function_name} Lambda"
            logger.error(error_message, extra={"payload": payload, "response": raw_response})
            raise
