import time
from unittest.mock import patch
from uuid import uuid4

import pytest

from lbz.authentication import User
from lbz.exceptions import Unauthorized
from tests.fixtures.rsa_pair import sample_public_key
from tests.utils import encode_token

allowed_audiences = [str(uuid4()), str(uuid4())]


@patch("lbz.jwt_utils.PUBLIC_KEYS", [sample_public_key])
@patch("lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences)
class TestAuthentication:
    def setup_class(self):
        with patch("lbz.jwt_utils.PUBLIC_KEYS", [sample_public_key]), patch(
            "lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences
        ):
            self.cognito_user = {
                "cognito:username": str(uuid4()),
                "custom:id": str(uuid4()),
                "email": f"{str(uuid4())}@{str(uuid4())}.com",
                "custom:1": str(uuid4()),
                "custom:2": str(uuid4()),
                "custom:3": str(uuid4()),
                "custom:4": str(uuid4()),
                "custom:5": str(uuid4()),
                "aud": allowed_audiences[0],
            }
            self.id_token = encode_token(self.cognito_user)
            self.pool_id = str(uuid4)
            self.sample_user = User(self.id_token)

    def test__repr__username(self):
        username = str(uuid4())
        sample_user = User(encode_token({"cognito:username": username}))
        assert sample_user.__repr__() == f"User username={username}"

    def test__repr__id(self):
        uid = str(uuid4())
        sample_user = User(encode_token({"custom:id": uid}))
        assert sample_user.__repr__() == f"User id={uid}"

    def test__repr__username_and_id_returns_id(self):
        username = str(uuid4())
        uid = str(uuid4())
        cognito_user = {"cognito:username": username, "custom:id": uid}
        sample_user = User(encode_token(cognito_user))
        assert sample_user.__repr__() == f"User id={uid}"

    def test_decoding_user(self):
        assert User(self.id_token)

    def test_decoding_user_raises_unauthorized_when_invalid_token(self):
        with pytest.raises(Unauthorized):
            User(self.id_token + "?")

    def test_decoding_user_raises_unauthorized_when_invalid_audience(self):
        with pytest.raises(Unauthorized), patch("lbz.jwt_utils.ALLOWED_AUDIENCES", [str(uuid4())]):
            User(self.id_token)

    def test_decoding_user_raises_unauthorized_when_invalid_public_key(self):
        with pytest.raises(Unauthorized), patch(
            "lbz.jwt_utils.PUBLIC_KEYS", [{**sample_public_key.copy(), "n": str(uuid4())}]
        ):
            User(self.id_token)

    def test_loading_user_parses_user_attributes(self):
        parsed = self.cognito_user.copy()
        del parsed["aud"]
        for k, v in parsed.items():
            assert (
                self.sample_user.__getattribute__(k.replace("cognito:", "").replace("custom:", ""))
                == v
            )

    def test_loading_user_does_not_parse_standard_claims(self):
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
        for k in standard_claims.keys():
            assert not hasattr(user, k)

    def test_user_raises_when_more_attributes_than_1000(self):
        with pytest.raises(RuntimeError):
            cognito_user = {str(uuid4()): str(uuid4()) for i in range(1001)}
            User(encode_token(cognito_user))

    def test_nth_cognito_client_validated_as_audience(self):
        allowed_audiences = [str(uuid4()) for _ in range(10)]
        with patch("lbz.jwt_utils.ALLOWED_AUDIENCES", allowed_audiences):
            assert User(encode_token({"aud": allowed_audiences[9]}))
