from lbz.lambdas import LambdaResult, lambda_error_response, lambda_ok_response


def test__lambda_ok_response__creates_expected_response() -> None:
    assert lambda_ok_response() == {"result": LambdaResult.OK}


def test__lambda_ok_response__creates_expected_response_with_data() -> None:
    assert lambda_ok_response({"some": "data"}) == {
        "result": LambdaResult.OK,
        "data": {"some": "data"},
    }


def test__lambda_error_response__creates_expected_response() -> None:
    expected_resp = {"result": LambdaResult.BAD_REQUEST, "message": "error was"}

    assert lambda_error_response(LambdaResult.BAD_REQUEST, "error was") == expected_resp


def test__lambda_error_response__creates_expected_response_with_error_code() -> None:
    expected_resp = {
        "result": LambdaResult.BAD_REQUEST,
        "message": "error was",
        "error_code": "ERR42",
    }

    assert lambda_error_response(LambdaResult.BAD_REQUEST, "error was", "ERR42") == expected_resp
