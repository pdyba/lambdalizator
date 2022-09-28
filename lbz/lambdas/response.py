from typing import TypedDict, Union

from lbz.lambdas.enums import LambdaResult


class LambdaResponse(TypedDict, total=False):
    result: str
    data: Union[list, dict, str]
    message: str
    error_code: str


def lambda_ok_response(data: dict = None) -> LambdaResponse:
    resp = LambdaResponse(result=LambdaResult.OK)
    if data is not None:
        resp["data"] = data
    return resp


def lambda_error_response(
    result: str, error_message: str, error_code: str = None
) -> LambdaResponse:
    err_response = LambdaResponse(result=result, message=error_message)
    if error_code:
        err_response["error_code"] = error_code
    return err_response
