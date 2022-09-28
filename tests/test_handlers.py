from unittest.mock import MagicMock, patch

import pytest

from lbz.handlers import BaseHandler


class MyBaseHandler(BaseHandler):
    def handle(self) -> str:
        return "something"


@patch.object(MyBaseHandler, "post_handle", autospec=True)
@patch.object(MyBaseHandler, "pre_handle", autospec=True)
def test_pre_and_post_hooks_are_triggered(pre_handle: MagicMock, post_handle: MagicMock) -> None:
    response = MyBaseHandler().react()

    assert response == "something"
    pre_handle.assert_called_once()
    post_handle.assert_called_once()


@patch.object(MyBaseHandler, "pre_handle", autospec=True)
def test_pre_handle_raises(pre_handle: MagicMock) -> None:
    pre_handle.side_effect = ValueError

    with pytest.raises(ValueError):
        MyBaseHandler().react()

    pre_handle.assert_called_once()


@patch.object(MyBaseHandler, "post_handle", autospec=True)
def test_post_handle_raises(post_handle: MagicMock) -> None:
    post_handle.side_effect = ValueError

    response = MyBaseHandler().react()

    assert response == "something"
    post_handle.assert_called_once()
