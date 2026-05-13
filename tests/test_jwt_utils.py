from datetime import datetime, timedelta, timezone
from os import environ
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt

from lbz.authz.authorizer import Authorizer
from lbz.exceptions import Unauthorized
from lbz.jwt_utils import decode_jwt, get_matching_jwk, validate_jwt_properties
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY, SAMPLE_PUBLIC_KEY


class TestGetMatchingJWK:
    @patch.object(jwt, "get_unverified_header", return_value=SAMPLE_PUBLIC_KEY)
    def test_get_matching_key(self, get_unverified_header_mock: MagicMock) -> None:
        assert get_matching_jwk("x") == SAMPLE_PUBLIC_KEY
        get_unverified_header_mock.assert_called_once()

    @patch.object(jwt, "get_unverified_header", return_value={"kid": "wrong-key"})
    def test_get_matching_key_fail(self, _get_unverified_header_mock: MagicMock) -> None:
        with pytest.raises(Unauthorized):
            get_matching_jwk("x")

    @patch.object(jwt, "get_unverified_header", MagicMock(return_value={}))
    def test_get_matching_missing_key(self) -> None:
        with pytest.raises(Unauthorized):
            get_matching_jwk("x")


class TestDecodeJWT:
    @patch.dict(environ, {"AUTH_ENABLED": "false"})
    def test_raises_error_when_auth_explicitly_disabled(self) -> None:
        with pytest.raises(RuntimeError, match="AUTH-dedicated features are explicitly disabled!"):
            decode_jwt("x")

    @patch("lbz.jwt_utils.get_matching_jwk", return_value={})
    def test_did_not_find_matching_jwk(
        self, get_matching_jwk_mock: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        with pytest.raises(Unauthorized):
            decode_jwt("x")
        get_matching_jwk_mock.assert_called_once_with("x")
        assert "Failed decoding JWT with following details" in caplog.text

    def test_proper_jwt(
        self, full_access_authz_payload: dict, full_access_auth_header: str
    ) -> None:
        decoded_jwt_data = decode_jwt(full_access_auth_header)
        assert decoded_jwt_data == full_access_authz_payload

    def test_expired_jwt(self) -> None:
        iat = int((datetime.now(timezone.utc) - timedelta(hours=12)).timestamp())
        exp = int((datetime.now(timezone.utc) - timedelta(hours=6)).timestamp())
        token_payload = {
            "exp": exp,
            "iat": iat,
            "iss": "test-issuer",
            "aud": "test-audience",
        }
        jwt_token = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        with pytest.raises(Unauthorized, match="Your token has expired. Please refresh it."):
            decode_jwt(jwt_token)

    def test_missing_correct_audiences(self, caplog: pytest.LogCaptureFixture) -> None:
        iat = int(datetime.now(timezone.utc).timestamp())
        exp = int((datetime.now(timezone.utc) + timedelta(hours=6)).timestamp())
        token_payload = {"exp": exp, "iat": iat, "iss": "test-issuer", "aud": "test"}
        jwt_token = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        with pytest.raises(Unauthorized):
            decode_jwt(jwt_token)
        assert "Failed decoding JWT with any of JWK - details" in caplog.text


class TestValidateJWTProperties:
    def test_raises_error_when_exp_field_is_missing(self) -> None:
        with pytest.raises(Unauthorized, match="The auth token could not be fully validated."):
            validate_jwt_properties({"allow": "*", "deny": {}})

    def test_raises_error_when_iss_field_is_missing(self) -> None:
        with pytest.raises(Unauthorized, match="The auth token could not be fully validated."):
            validate_jwt_properties({"allow": "*", "deny": {}, "exp": 1778710870})

    def test_raises_error_when_not_allowed_iss(self, full_access_authz_payload: dict) -> None:
        with pytest.raises(Unauthorized, match="The auth token could not be fully validated."):
            validate_jwt_properties({**full_access_authz_payload, "iss": "test2"})
