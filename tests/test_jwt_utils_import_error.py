from unittest.mock import patch

import pytest


def not_working_test() -> None:  # TODO: finish me! - lbz/jwt_utils.py:26 mocking hell
    with patch("lbz.jwt_utils.env", {}):
        with pytest.raises(ValueError):
            from lbz.jwt_utils import PUBLIC_KEYS  # pylint: disable=import-outside-toplevel

            print(PUBLIC_KEYS)
