from __future__ import annotations

from typing import Any, TypedDict

from lbz.lambdas.enums import LambdaResult


class LambdaResponse(TypedDict, total=False):
    result: str
    data: Any
    message: str
    error_code: str


def lambda_ok_response(data: Any = None) -> LambdaResponse:
    resp = LambdaResponse(result=LambdaResult.OK)
    if data is not None:
        resp["data"] = data
    return resp


def lambda_error_response(
    result: str, error_message: str, error_code: str | None = None
) -> LambdaResponse:
    err_response = LambdaResponse(result=result, message=error_message)
    if error_code is not None:
        err_response["error_code"] = error_code
    return err_response
