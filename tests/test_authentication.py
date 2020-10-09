import json

import pytest

from uuid import uuid4

from jose import jwt

from lbz.authentication import User
from lbz.exceptions import Unauthorized

from tests.fixtures.rsa_pair import sample_private_key, sample_public_key


class TestCognitoAuthentication:
    def setup_class(self):
        self.username = str(uuid4())
        self.id = str(uuid4())
        self.cognito_user = {
            "cognito:username": self.username,
            "custom:id": self.id,
            "email": f"{str(uuid4())}@{str(uuid4())}.com",
            "custom:1": str(uuid4()),
            "custom:2": str(uuid4()),
            "custom:3": str(uuid4()),
            "custom:4": str(uuid4()),
            "custom:5": str(uuid4()),
        }
        self.id_token = jwt.encode(
            self.cognito_user,
            sample_private_key,
            "RS256",
        )
        self.pool_id = str(uuid4)
        self.sample_user = User(self.id_token, sample_public_key, self.pool_id)

    def test__repr__username(self):
        username = str(uuid4())
        id_token = jwt.encode(
            {
                "cognito:username": username,
            },
            sample_private_key,
            "RS256",
        )
        sample_user = User(id_token, sample_public_key, str(uuid4))
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
        pool_id = str(uuid4)
        sample_user = User(id_token, sample_public_key, pool_id)
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
        sample_user = User(id_token, sample_public_key, str(uuid4))
        assert sample_user.__repr__() == f"User id={uid}"

    def test_decoding_user(self):
        assert User(self.id_token, sample_public_key, self.pool_id)

    def test_decoding_user_raises_unauthorized_when_invalid_token(self):
        with pytest.raises(Unauthorized):
            User(self.id_token + "?", sample_public_key, self.pool_id)

    def test_decoding_user_raises_unauthorized_when_invalid_audience(self):
        with pytest.raises(Unauthorized):
            User(self.id_token + "?", sample_public_key, "")

    def test_decoding_user_raises_unauthorized_when_invalid_public_key(self):
        invalid_public_key = {**sample_public_key.copy(), "n": str(uuid4())}
        with pytest.raises(Unauthorized):
            User(self.id_token, invalid_public_key, self.pool_id)

    def test_loading_user_parses_user_attributes(self):
        for k, v in self.cognito_user.items():
            assert (
                self.sample_user.__getattribute__(k.replace("cognito:", "").replace("custom:", ""))
                == v
            )

    def test_loading_user_with_public_key_as_string(self):
        assert User(self.id_token, json.dumps(sample_public_key), self.pool_id)

    def test_user_raises_when_more_attributes_than_1000(self):
        with pytest.raises(RuntimeError):
            self.cognito_user = {str(uuid4()): str(uuid4()) for i in range(1001)}
            self.id_token = jwt.encode(
                self.cognito_user,
                sample_private_key,
                "RS256",
            )
            User(self.id_token, sample_public_key, str(uuid4()))
