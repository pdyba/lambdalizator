import json
import random

import pytest

from uuid import uuid4

from jose import jwt

from lbz.authentication import User
from lbz.exceptions import Unauthorized

from tests.fixtures.rsa_pair import sample_private_key, sample_public_key


class TestCognitoAuthentication:
    def setup_class(self):
        self.allowed_cognito_clients = [str(uuid4()), str(uuid4())]
        self.cognito_user = {
            "cognito:username": str(uuid4()),
            "custom:id": str(uuid4()),
            "email": f"{str(uuid4())}@{str(uuid4())}.com",
            "custom:1": str(uuid4()),
            "custom:2": str(uuid4()),
            "custom:3": str(uuid4()),
            "custom:4": str(uuid4()),
            "custom:5": str(uuid4()),
            "aud": self.allowed_cognito_clients[0],
        }
        self.id_token = jwt.encode(
            self.cognito_user,
            sample_private_key,
            "RS256",
        )
        self.pool_id = str(uuid4)
        self.sample_user = User(self.id_token, sample_public_key, self.allowed_cognito_clients)

    def test__repr__username(self):
        username = str(uuid4())
        id_token = jwt.encode(
            {
                "cognito:username": username,
            },
            sample_private_key,
            "RS256",
        )
        sample_user = User(id_token, sample_public_key, self.allowed_cognito_clients)
        assert sample_user.__repr__() == f"User username={username}"

    def test__repr__id(self):
        uid = str(uuid4())
        id_token = jwt.encode(
            {
                "custom:id": uid,
            },
            sample_private_key,
            "RS256",
        )
        sample_user = User(id_token, sample_public_key, self.allowed_cognito_clients)
        assert sample_user.__repr__() == f"User id={uid}"

    def test__repr__username_and_id_returns_id(self):
        username = str(uuid4())
        uid = str(uuid4())
        cognito_user = {
            "cognito:username": username,
            "custom:id": uid,
        }
        id_token = jwt.encode(
            cognito_user,
            sample_private_key,
            "RS256",
        )
        sample_user = User(id_token, sample_public_key, self.allowed_cognito_clients)
        assert sample_user.__repr__() == f"User id={uid}"

    def test_decoding_user(self):
        assert User(self.id_token, sample_public_key, self.allowed_cognito_clients)

    def test_decoding_user_raises_unauthorized_when_invalid_token(self):
        with pytest.raises(Unauthorized):
            User(self.id_token + "?", sample_public_key, self.allowed_cognito_clients)

    def test_decoding_user_raises_unauthorized_when_invalid_audience(self):
        with pytest.raises(Unauthorized):
            User(
                self.id_token,
                sample_public_key,
                [self.allowed_cognito_clients[0] + "?"],
            )

    def test_decoding_user_raises_unauthorized_when_invalid_public_key(self):
        invalid_public_key = {**sample_public_key.copy(), "n": str(uuid4())}
        with pytest.raises(Unauthorized):
            User(self.id_token, invalid_public_key, self.allowed_cognito_clients)

    def test_loading_user_parses_user_attributes(self):
        parsed = self.cognito_user.copy()
        del parsed["aud"]
        for k, v in parsed.items():
            assert (
                self.sample_user.__getattribute__(k.replace("cognito:", "").replace("custom:", ""))
                == v
            )

    def test_loading_user_does_not_parse_standard_claims(self):
        standard_claims = {
            "sub": str(uuid4()),
            "aud": self.allowed_cognito_clients[0],
            "token_use": "id",
            "auth_time": random.randrange(9999999999),
            "iss": str(uuid4()),
            "exp":  random.randrange(9999999999),
            "iat": random.randrange(9999999999),
        }

        id_token = jwt.encode(
            {
                "cognito:username": str(uuid4()),
                "custom:id": str(uuid4()),
                **standard_claims,
            },
            sample_private_key,
            "RS256",
        )
        user = User(id_token, sample_public_key, self.allowed_cognito_clients)
        for k in standard_claims.keys():
            assert not hasattr(user, k)

    def test_loading_user_with_public_key_as_string(self):
        assert User(self.id_token, json.dumps(sample_public_key), self.allowed_cognito_clients)

    def test_user_raises_when_more_attributes_than_1000(self):
        with pytest.raises(RuntimeError):
            cognito_user = {str(uuid4()): str(uuid4()) for i in range(1001)}
            id_token = jwt.encode(
                cognito_user,
                sample_private_key,
                "RS256",
            )
            User(id_token, sample_public_key, self.allowed_cognito_clients)

    def test_nth_cognito_client_validated_as_audience(self):
        allowed_cognito_clients = [str(uuid4()) for i in range(10)]
        id_token = jwt.encode(
            {"aud": allowed_cognito_clients[9]},
            sample_private_key,
            "RS256",
        )
        assert User(id_token, sample_public_key, allowed_cognito_clients)
