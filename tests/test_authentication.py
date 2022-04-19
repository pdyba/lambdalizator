# coding=utf-8
import os
import time
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from lbz.authentication import User
from lbz.exceptions import Unauthorized
from lbz.jwt_utils import ALLOWED_ISS
from tests.fixtures.rsa_pair import SAMPLE_PUBLIC_KEY
from tests.utils import encode_token

allowed_audiences = [str(uuid4()), str(uuid4())]


class TestAuthentication:
    def setup_class(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.cognito_user = {
            "cognito:username": str(uuid4()),
            "email": f"{str(uuid4())}@{str(uuid4())}.com",
            "custom:id": str(uuid4()),
            "custom:1": str(uuid4()),
            "custom:2": str(uuid4()),
            "aud": os.environ["ALLOWED_AUDIENCES"].split(",")[
                0
            ],  # moved due pylint and minimising scope of PR
            "iss": ALLOWED_ISS,
            "exp": int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "custom:3": str(uuid4()),
            "custom:4": str(uuid4()),
            "custom:5": str(uuid4()),
        }
        self.id_token = encode_token(self.cognito_user)
        self.pool_id = str(uuid4)
        self.sample_user = User(self.id_token)

    def test__repr__username(self, jwt_partial_payload) -> None:
        username = str(uuid4())
        sample_user = User(encode_token({"cognito:username": username, **jwt_partial_payload}))
        assert sample_user.__repr__() == f"User username={username}"

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

    def test_loading_user_parses_user_attributes(self) -> None:
        parsed = self.cognito_user.copy()
        for key in ["aud", "iss", "exp", "iat"]:
            parsed.pop(key, None)
        for key, expected_value in parsed.items():
            value = self.sample_user.__getattribute__(
                key.replace("cognito:", "").replace("custom:", "")
            )
            assert value == expected_value

    def test_loading_user_does_not_parse_standard_claims(self, jwt_partial_payload) -> None:
        current_ts = int(time.time())
        standard_claims = {
            **jwt_partial_payload,
            "sub": str(uuid4()),
            "token_use": "id",
            "auth_time": current_ts,
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
            assert User(encode_token({**self.cognito_user, "aud": test_allowed_audiences[9]}))
