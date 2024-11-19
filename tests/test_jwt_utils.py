from copy import deepcopy
from datetime import datetime, timedelta, timezone
from os import environ
from unittest.mock import MagicMock, patch

import jwt
import pytest

from lbz.authz.authorizer import ALL
from lbz.exceptions import Unauthorized
from lbz.jwt_utils import decode_jwt, encode_jwt, get_matching_public_jwk, validate_jwt_properties
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY, SAMPLE_PUBLIC_KEY


class TestGetMatchingPublicJWK:
    @patch.object(jwt, "get_unverified_header", return_value=SAMPLE_PUBLIC_KEY)
    def test_get_matching_key(self, get_unverified_header_mock: MagicMock) -> None:
        assert get_matching_public_jwk("x") == SAMPLE_PUBLIC_KEY
        get_unverified_header_mock.assert_called_once()

    @patch.object(jwt, "get_unverified_header", return_value={"kid": "wrong-key"})
    def test_get_matching_key_fail(self, _get_unverified_header_mock: MagicMock) -> None:
        with pytest.raises(Unauthorized):
            get_matching_public_jwk("x")

    @patch.object(jwt, "get_unverified_header", MagicMock(return_value={}))
    def test_get_matching_missing_key(self) -> None:
        with pytest.raises(Unauthorized):
            get_matching_public_jwk("x")


class TestDecodeJWT:
    @patch.dict(environ, {"AUTH_ENABLED": "false"})
    def test_raises_error_when_auth_explicitly_disabled(self) -> None:
        with pytest.raises(RuntimeError, match="AUTH-dedicated features are explicitly disabled!"):
            decode_jwt("x")

    def test_did_not_find_matching_jwk(self) -> None:
        private_key = deepcopy(SAMPLE_PRIVATE_KEY)
        private_key["kid"] = "totally-different-key"
        jwt_token = encode_jwt(data={}, private_jwk=private_key)

        with pytest.raises(Unauthorized):
            decode_jwt(jwt_token)

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
        jwt_token = encode_jwt(token_payload, SAMPLE_PRIVATE_KEY)

        with pytest.raises(Unauthorized, match="Your token has expired. Please refresh it."):
            decode_jwt(jwt_token)

    def test_missing_correct_audiences(self) -> None:
        iat = int(datetime.now(timezone.utc).timestamp())
        exp = int((datetime.now(timezone.utc) + timedelta(hours=6)).timestamp())
        token_payload = {"exp": exp, "iat": iat, "iss": "test-issuer", "aud": "test"}
        jwt_token = encode_jwt(token_payload, SAMPLE_PRIVATE_KEY)

        with pytest.raises(Unauthorized):
            decode_jwt(jwt_token)


class TestEncodeJWT:
    def test_encodes_provided_data_returning_predictable_token(self) -> None:
        token = encode_jwt(
            data={"allow": {ALL: ALL}, "deny": {}},
            private_jwk=SAMPLE_PRIVATE_KEY,
        )

        assert token == (
            "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk0OTRhZDc1LTNmNTQtNDE1NS04NGZhLWMxYTE3ZGEyMmIzNSIsInR5c"
            "CI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.nDqCxO2Q1iXpxzbH7syxuyqw7kCY0sDfi"
            "9RX-VSUMTRN5aWTLt1bcPw4oN_jx89-YHBzDwnwBc07RsMgpFuo4zz2LU9PF0ciYxMNX-atTNsaIn05NkXT08"
            "au2AYb0DRCDS76MZ4QNi-4mRpLrj1SD4mSCwGtc2WNw9f0J0Vm4ZCYPVW6BqpcHcaFXzcFZ6EIoooaK6GvdTO"
            "jy498lWsAXjAen2U6Jles_BwFjqW1lW_ky4WV4J9NnK3v5wWKgR1Pg4R4LpnhIXe0dU_l64JHoJA3YcYxl-qi"
            "lHfoBduc3La4kRKk7FAQDIqbOv4uN03BIoDXLH5t2uJ1Sm79Pe0ngGd5pSBmfUDKOGsHtx_3_9ZKfp-E2IVS0"
            "C7r36p4Ue0gKQzn0pXxa591bxm_puJAQ399SdbmlOJsM2cVFYAtlUQvWgErc57WcUJ0Qe4jEycury7hagNbP2"
            "fLn-7Gg4gZHiZ_Ul7L6GukbDfCHnhxSS4P3t3cVtWuslZi16hDhNbOTKD95y7PXvHePvI57ALV2v0RecQ5Blw"
            "urt1OuDRSjCYXyO6U4Y9MBHcd1wMtDoVW0jjvjXvqkEhuB52Zajh_yTNnJo0OAHpuK5wldVpECGFVx1rkW1yp"
            "KqlukGIgD--m6ElKnl6jw5VWSbdh2TJsZHnzjovbQUeqZOeMxwX6SE8"
        )


class TestValidateJWTProperties:
    def test_raises_error_when_exp_field_is_missing(self) -> None:
        with pytest.raises(Unauthorized):
            validate_jwt_properties({"allow": "*", "deny": {}})

    def test_raises_error_when_iss_field_is_missing(self) -> None:
        with pytest.raises(Unauthorized):
            validate_jwt_properties({"allow": "*", "deny": {}, "exp": 1778710870})

    def test_raises_error_when_not_allowed_iss(self, full_access_authz_payload: dict) -> None:
        with pytest.raises(Unauthorized):
            validate_jwt_properties({**full_access_authz_payload, "iss": "test2"})
