from unittest.mock import MagicMock, patch

from lbz.handlers import BaseHandler


class MyBaseHandler(BaseHandler):
    def handle(self) -> None:
        return None


@patch.object(MyBaseHandler, "post_handle")
@patch.object(MyBaseHandler, "pre_handle")
def test_pre_and_post_hooks_are_triggered(pre_handle: MagicMock, post_handle: MagicMock) -> None:
    response = MyBaseHandler().react()

    assert response is None
    pre_handle.assert_called_once()
    post_handle.assert_called_once()
