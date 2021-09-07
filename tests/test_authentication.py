# coding=utf-8
import time
from unittest.mock import patch
from uuid import uuid4

import pytest

from lbz.authentication import User
from lbz.exceptions import Unauthorized
from tests.fixtures.rsa_pair import SAMPLE_PUBLIC_KEY
from tests.utils import encode_token, allowed_audiences


@patch("lbz.jwt_utils.PUBLIC_KEYS", [SAMPLE_PUBLIC_KEY])
@patch("lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences)
class TestAuthentication:
    @pytest.fixture(autouse=True)
    def setup_class(self, user_token) -> None:
        with patch("lbz.jwt_utils.PUBLIC_KEYS", [SAMPLE_PUBLIC_KEY]), patch(
            "lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences
        ):
            self.id_token = user_token  # pylint: disable=attribute-defined-outside-init
            self.sample_user = User(  # pylint: disable=attribute-defined-outside-init
                self.id_token
            )

    def test__repr__username(self, user_username) -> None:
        assert self.sample_user.__repr__() == f"User username={user_username}"

        sample_user_2 = User(encode_token({"type": "x"}))
        assert sample_user_2.__repr__() == "User"

    def test_decoding_user(self) -> None:
        assert User(self.id_token)

    def test_decoding_user_raises_unauthorized_when_invalid_token(self) -> None:
        with pytest.raises(Unauthorized):
            User(self.id_token + "?")

    def test_decoding_user_raises_unauthorized_when_invalid_audience(self) -> None:
        with pytest.raises(Unauthorized), patch("lbz.jwt_utils.ALLOWED_AUDIENCES", [str(uuid4())]):
            User(self.id_token)

    def test_decoding_user_raises_unauthorized_when_invalid_public_key(self) -> None:
        with pytest.raises(Unauthorized), patch(
            "lbz.jwt_utils.PUBLIC_KEYS",
            [{**SAMPLE_PUBLIC_KEY.copy(), "n": str(uuid4())}],
        ):
            User(self.id_token)

    def test_loading_user_parses_user_attributes(self, user_cogniot) -> None:
        parsed = user_cogniot.copy()
        del parsed["aud"]
        for key, expected_value in parsed.items():
            value = self.sample_user.__getattribute__(
                key.replace("cognito:", "").replace("custom:", "")
            )
            assert value == expected_value

    def test_loading_user_does_not_parse_standard_claims(self) -> None:
        current_ts = int(time.time())
        standard_claims = {
            "sub": str(uuid4()),
            "aud": allowed_audiences[0],
            "token_use": "id",
            "auth_time": current_ts,
            "iss": str(uuid4()),
            "exp": current_ts + 1000,
            "iat": current_ts,
        }

        id_token = encode_token(
            {
                "cognito:username": str(uuid4()),
                "custom:id": str(uuid4()),
                **standard_claims,
            }
        )
        user = User(id_token)
        for key in standard_claims:
            assert not hasattr(user, key)

    def test_user_raises_when_more_attributes_than_1000(self) -> None:
        with pytest.raises(RuntimeError):
            cognito_user = {str(uuid4()): str(uuid4()) for i in range(1001)}
            User(encode_token(cognito_user))

    def test_nth_cognito_client_validated_as_audience(self) -> None:
        test_allowed_audiences = [str(uuid4()) for _ in range(10)]
        with patch("lbz.jwt_utils.ALLOWED_AUDIENCES", test_allowed_audiences):
            assert User(encode_token({"aud": test_allowed_audiences[9]}))
