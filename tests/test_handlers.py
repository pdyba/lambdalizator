import logging
from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from lbz.handlers import BaseHandler
from lbz.type_defs import LambdaContext


class MyBaseHandler(BaseHandler):
    def handle(self) -> str:
        return "something"


@patch.object(MyBaseHandler, "post_handle", autospec=True)
@patch.object(MyBaseHandler, "pre_handle", autospec=True)
def test__react__triggers_both_pre_and_post_handle(
    pre_handle: MagicMock, post_handle: MagicMock
) -> None:
    response = MyBaseHandler({}, LambdaContext()).react()

    assert response == "something"
    pre_handle.assert_called_once()
    post_handle.assert_called_once()


@patch.object(MyBaseHandler, "post_handle", autospec=True)
@patch.object(MyBaseHandler, "pre_handle", autospec=True)
def test__react__raises_error_when_pre_handle_fails(
    pre_handle: MagicMock, post_handle: MagicMock
) -> None:
    pre_handle.side_effect = ValueError

    with pytest.raises(ValueError):
        MyBaseHandler({}, LambdaContext()).react()

    pre_handle.assert_called_once()
    post_handle.assert_not_called()


@patch.object(MyBaseHandler, "post_handle", autospec=True)
def test__react__only_logs_error_when_post_handle_fails(
    post_handle: MagicMock, caplog: LogCaptureFixture
) -> None:
    post_handle.side_effect = ValueError("xxxx")

    response = MyBaseHandler({}, LambdaContext()).react()

    assert response == "something"
    post_handle.assert_called_once()

    assert caplog.record_tuples == [("lbz.handlers", logging.ERROR, "xxxx")]
