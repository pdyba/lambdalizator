from typing import Any, Optional, TypedDict

from lbz.lambdas.enums import LambdaResult


class LambdaResponse(TypedDict, total=False):
    result: str
    data: Optional[Any]
    message: Optional[str]
    error_code: Optional[str]


def lambda_ok_response(data: dict = None) -> LambdaResponse:
    resp = LambdaResponse(result=LambdaResult.OK)
    if data is not None:
        resp["data"] = data
    return resp


def lambda_error_response(
    result: str, error_message: str, error_code: str = None
) -> LambdaResponse:
    return LambdaResponse(result=result, message=error_message, error_code=error_code)
