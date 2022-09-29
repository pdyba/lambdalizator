import json
from typing import Any, Iterable, Optional, Type

from lbz.aws_boto3 import client
from lbz.lambdas.enums import LambdaResult, LambdaSource
from lbz.lambdas.exceptions import LambdaError
from lbz.lambdas.response import LambdaResponse
from lbz.misc import get_logger

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
        raw_response = client.lambda_.invoke(
            FunctionName=function_name,
            Payload=json.dumps(payload, cls=cls.json_encoder).encode("utf-8"),
            InvocationType="Event" if asynchronous else "RequestResponse",
        )

        if asynchronous:
            # Lambda invoked asynchronously only includes a status code in the response
            return {"result": LambdaResult.ACCEPTED}

        try:
            response: LambdaResponse = json.loads(raw_response["Payload"].read().decode("utf-8"))
        except Exception:
            message = "Invalid response received from %s Lambda (op: %s)"
            logger.error(message, function_name, op, extra=dict(data=data, response=raw_response))
            raise

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
