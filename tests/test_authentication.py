import json
import time
from os import environ
from unittest.mock import patch
from uuid import uuid4

import pytest

from lbz.authentication import User
from lbz.exceptions import Unauthorized
from lbz.jwt_utils import encode_jwt
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY, SAMPLE_PUBLIC_KEY


def test__repr__username(jwt_partial_payload: dict) -> None:
    username = str(uuid4())
    sample_user = User(
        encode_jwt({"cognito:username": username, **jwt_partial_payload}, SAMPLE_PRIVATE_KEY),
    )
    assert repr(sample_user) == f"User username={username}"


def test_decoding_user(user_token: str) -> None:
    assert User(user_token)


def test_decoding_user_raises_unauthorized_when_invalid_token(user_token: str) -> None:
    with pytest.raises(Unauthorized):
        User(user_token + "?")


@patch.dict(environ, {"ALLOWED_AUDIENCES": str(uuid4())})
def test_decoding_user_raises_unauthorized_when_invalid_audience(user_token: str) -> None:
    with pytest.raises(Unauthorized):
        User(user_token)


@patch.dict(
    environ,
    {
        "ALLOWED_PUBLIC_KEYS": json.dumps(
            {"keys": [{**SAMPLE_PUBLIC_KEY.copy(), "n": str(uuid4())}]}
        )
    },
)
def test_decoding_user_raises_unauthorized_when_invalid_public_key(user_token: str) -> None:
    with pytest.raises(Unauthorized):
        User(user_token)


def test_loading_user_parses_user_attributes(user_cognito: dict, user: User) -> None:
    parsed = user_cognito.copy()
    for key in ("aud", "iss", "exp", "iat"):
        parsed.pop(key, None)
    for key, expected_value in parsed.items():
        key_without_prefix = key.replace("cognito:", "").replace("custom:", "")
        value = getattr(user, key_without_prefix)
        assert value == expected_value


def test_loading_user_does_not_parse_standard_claims(jwt_partial_payload: dict) -> None:
    current_ts = int(time.time())
    standard_claims = {
        **jwt_partial_payload,
        "sub": str(uuid4()),
        "token_use": "id",
        "auth_time": current_ts,
    }

    id_token = encode_jwt(
        {
            "cognito:username": str(uuid4()),
            "custom:id": str(uuid4()),
            **standard_claims,
        },
        SAMPLE_PRIVATE_KEY,
    )
    user = User(id_token)
    for key in standard_claims:
        assert not hasattr(user, key)


def test_user_raises_when_more_attributes_than_1000(allowed_audiences: list[str]) -> None:
    cognito_user = {str(uuid4()): str(uuid4()) for i in range(1001)}

    with pytest.raises(RuntimeError):
        User(encode_jwt({**cognito_user, "aud": allowed_audiences[0]}, SAMPLE_PRIVATE_KEY))


def test_nth_cognito_client_validated_as_audience(user_cognito: dict) -> None:
    test_allowed_audiences = [str(uuid4()) for _ in range(10)]
    with patch.dict(environ, {"ALLOWED_AUDIENCES": ",".join(test_allowed_audiences)}):
        assert User(
            encode_jwt({**user_cognito, "aud": test_allowed_audiences[9]}, SAMPLE_PRIVATE_KEY)
        )
