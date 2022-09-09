from __future__ import annotations

from typing import Optional, TypedDict

from lbz.lambdas.enums import LambdaResult


class LambdaResponse(TypedDict, total=False):
    result: str
    data: Optional[dict]
    message: Optional[str]
    error: Optional[str]
    error_code: Optional[str]


def lambda_ok_response(data: dict = None) -> LambdaResponse:
    resp = LambdaResponse(result=LambdaResult.OK)
    if data is not None:
        resp["data"] = data
    return resp


def lambda_error_response(result: str, error: str, error_code: str = None) -> LambdaResponse:
    return LambdaResponse(result=result, error=error, error_code=error_code)
