import json
from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, Union, cast

from lbz.lambdas.enums import LambdaSource

if TYPE_CHECKING:
    from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
else:
    InvocationResponseTypeDef = dict

from lbz.aws_boto3 import client
from lbz.exceptions import LambdaError
from lbz.lambdas.enums import LambdaResult
from lbz.misc import get_logger

logger = get_logger(__name__)


class SetsEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (set, frozenset)):
            return list(o)
        return json.JSONEncoder.default(self, o)


class LambdaClient:
    json_encoder: Type[json.JSONEncoder] = SetsEncoder
    op_key: str = "op"
    data_key: str = "data"
    result_key: str = "result"

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
    ) -> Union[InvocationResponseTypeDef, dict]:
        allowed_error_results = set(allowed_error_results or []) & set(LambdaResult.soft_errors())

        payload = {"invoke_type": LambdaSource.DIRECT, cls.op_key: op, cls.data_key: data}
        response = client.lambda_.invoke(
            FunctionName=function_name,
            Payload=json.dumps(payload, cls=cls.json_encoder).encode("utf-8"),
            InvocationType="Event" if asynchronous else "RequestResponse",
        )

        if asynchronous:
            # Lambda invoked asynchronously only includes a status code in the response
            return {"result": LambdaResult.ACCEPTED}

        try:
            response = json.loads(response["Payload"].read().decode("utf-8"))
        except Exception:
            error_msg = "Invalid response received from %s Lambda (op: %s)"
            logger.error(error_msg, function_name, op, extra=dict(data=data, response=response))
            raise

        lambda_result: str = cast(str, response.get(cls.result_key))
        if lambda_result in LambdaResult.successes():
            return response
        if lambda_result in allowed_error_results:
            return response
        if raise_if_error_resp:
            raise LambdaError(function_name, op, lambda_result, response)

        # f-string used directly to keep messages unique, especially from the Sentry perspective
        error_message = f"Error response from {function_name} Lambda (op: {op}): {lambda_result}"
        logger.error(error_message, extra=dict(data=data, response=response))
        return response
