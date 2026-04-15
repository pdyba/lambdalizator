import pytest

from lbz.exceptions import (
    BadRequestError,
    LambdaFWClientException,
    LambdaFWException,
    LambdaFWServerException,
    ServerError,
    UnsupportedMethod,
    all_lbz_errors,
)


def test__lambda_fw_exception__respects_attributes_declared_on_inherited_class_level() -> None:
    class TestException(LambdaFWException):
        message = "No error message"
        status_code = 444
        error_code = "TEST_ERR"

    exception = TestException()

    assert str(exception) == "[444] TEST_ERR - No error message"
    assert exception.message == "No error message"
    assert exception.status_code == 444
    assert exception.error_code == "TEST_ERR"
    assert exception.extra == {}


def test__lambda_fw_exception__respects_values_provided_during_initialization() -> None:
    exception = LambdaFWException(
        message="Test error message",
        status_code=555,
        error_code="TEST_ERR",
        extra={"fun": "stuff"},
    )

    assert str(exception) == "[555] TEST_ERR - Test error message"
    assert exception.message == "Test error message"
    assert exception.status_code == 555
    assert exception.error_code == "TEST_ERR"
    assert exception.extra == {"fun": "stuff"}


def test__unsupported_method__builds_message_based_on_method_provided_from_outside() -> None:
    exception = UnsupportedMethod("GET")

    assert exception.message == "Unsupported method: GET"
    assert exception.error_code is None
    assert exception.status_code == 405


@pytest.mark.parametrize("custom_exception", set(all_lbz_errors()) - {UnsupportedMethod})
def test__custom_exception__contains_message_and_status_code_according_to_its_docstring(
    custom_exception: type[LambdaFWException],
) -> None:
    exception = custom_exception()
    code, message = custom_exception().__doc__.split("-", maxsplit=1)  # type: ignore[union-attr]

    assert issubclass(custom_exception, LambdaFWException)
    assert exception.message == message.strip()
    assert exception.status_code == int(code.strip())


def test__all_lbz_errors__returns_all_subclasses_of_lambda_fw_exception() -> None:
    result = set(all_lbz_errors())

    assert BadRequestError in result
    assert ServerError in result
    assert LambdaFWException not in result
    assert LambdaFWClientException not in result
    assert LambdaFWServerException not in result
