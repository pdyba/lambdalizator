from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest
from jose import jwt

from lbz.authz.authorizer import Authorizer
from lbz.exceptions import Unauthorized
from lbz.jwt_utils import get_matching_jwk, decode_jwt
from tests import SAMPLE_PUBLIC_KEY, SAMPLE_PRIVATE_KEY

BAD_PUBLIC_KEY = {
    "kid": "wrong-key",
}


class TestGetMatchingJWK:
    @patch.object(jwt, "get_unverified_header", return_value=SAMPLE_PUBLIC_KEY)
    def test_get_matching_key(self, get_unverified_header_mock: MagicMock) -> None:
        assert get_matching_jwk("x") == SAMPLE_PUBLIC_KEY
        get_unverified_header_mock.assert_called_once()

    @patch.object(jwt, "get_unverified_header", return_value=BAD_PUBLIC_KEY)
    def test_get_matching_key_fail(self, _get_unverified_header_mock: MagicMock) -> None:
        with pytest.raises(Unauthorized):
            get_matching_jwk("x")

    @patch.object(jwt, "get_unverified_header", return_value={})
    def test_get_matching_missing_key(self, _get_unverified_header_mock: MagicMock) -> None:
        with pytest.raises(Unauthorized):
            get_matching_jwk("x")


class TestDecodeJWT:
    @patch("lbz.jwt_utils.get_matching_jwk", return_value={})
    def test_missing_public_keys(self, get_matching_jwk_mock: MagicMock) -> None:
        with pytest.raises(Unauthorized, match=r"\[401\] Not enough segments"):
            decode_jwt("x")
        get_matching_jwk_mock.assert_called_once_with("x")

    @patch("lbz.jwt_utils.get_matching_jwk", return_value={})
    def test_invalid_type(self, get_matching_jwk_mock: MagicMock) -> None:
        msg = "error occurred during decoding"
        with pytest.raises(RuntimeError, match=msg):
            decode_jwt({"a"})
        get_matching_jwk_mock.assert_called_once_with({"a"})

    def test_proper_jwt(self, full_access_authz_payload, full_access_auth_header) -> None:
        decoded_jwt_data = decode_jwt(full_access_auth_header)
        assert decoded_jwt_data == full_access_authz_payload

    def test_expired_jwt(self) -> None:
        iat = int((datetime.utcnow() - timedelta(hours=12)).timestamp())
        exp = int((datetime.utcnow() - timedelta(hours=6)).timestamp())
        token_payload = {
            "exp": exp,
            "iat": iat,
            "iss": "test-issuer",
        }
        jwt_token = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        with pytest.raises(Unauthorized, match="Your token has expired. Please refresh it."):
            decode_jwt(jwt_token)


@patch("lbz.jwt_utils.ALLOWED_AUDIENCES", [])
class TestDecodeJWTMissingAudiences:
    @patch.object(jwt, "decode")
    @patch("lbz.jwt_utils.get_matching_jwk", return_value={})
    def test_missing_audiences(
        self, get_matching_jwk_mock: MagicMock, decode_mock: MagicMock
    ) -> None:
        with pytest.raises(Unauthorized):
            decode_jwt("x")
        get_matching_jwk_mock.assert_called_once_with("x")
        decode_mock.assert_not_called()


class TestDecodeJWTAudiencesMissMatch:
    def test_missing_audiences(self) -> None:
        iat = int(datetime.utcnow().timestamp())
        exp = int((datetime.utcnow() + timedelta(hours=6)).timestamp())
        token_payload = {"exp": exp, "iat": iat, "iss": "test-issuer", "aud": "test"}
        jwt_token = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        with pytest.raises(Unauthorized, match="Invalid audience"):
            decode_jwt(jwt_token)


@patch("lbz.jwt_utils.PUBLIC_KEYS", [])
class TestDecodeJWTMissingKEy:
    def test_missing_public_keys(self) -> None:
        with pytest.raises(RuntimeError):
            decode_jwt("x")
