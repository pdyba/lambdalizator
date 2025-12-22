import logging
from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from lbz.brokers import BaseBroker
from lbz.type_defs import LambdaContext


class CustomBroker(BaseBroker):
    def handle(self) -> str:
        return "something"


@patch.object(CustomBroker, "post_handle", autospec=True)
@patch.object(CustomBroker, "pre_handle", autospec=True)
def test__react__triggers_both_pre_and_post_handle(
    pre_handle: MagicMock, post_handle: MagicMock
) -> None:
    response = CustomBroker({}, LambdaContext()).react()

    assert response == "something"
    pre_handle.assert_called_once()
    post_handle.assert_called_once()


@patch.object(CustomBroker, "post_handle", autospec=True)
@patch.object(CustomBroker, "pre_handle", autospec=True)
def test__react__raises_error_when_pre_handle_fails(
    pre_handle: MagicMock, post_handle: MagicMock
) -> None:
    pre_handle.side_effect = ValueError

    with pytest.raises(ValueError):
        CustomBroker({}, LambdaContext()).react()

    pre_handle.assert_called_once()
    post_handle.assert_not_called()


@patch.object(CustomBroker, "post_handle", autospec=True)
def test__react__only_logs_error_when_post_handle_fails(
    post_handle: MagicMock, caplog: LogCaptureFixture
) -> None:
    post_handle.side_effect = ValueError("xxxx")

    response = CustomBroker({}, LambdaContext()).react()

    assert response == "something"
    post_handle.assert_called_once()

    assert caplog.record_tuples == [("lbz.brokers", logging.ERROR, "xxxx")]
