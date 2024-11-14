import jwt
from jwt import PyJWK
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidTokenError

from lbz._cfg import ALLOWED_AUDIENCES, ALLOWED_ISS, ALLOWED_PUBLIC_KEYS, AUTH_ENABLED
from lbz.exceptions import Unauthorized
from lbz.misc import get_logger

logger = get_logger(__name__)


def get_matching_jwk(encoded_token: str) -> dict:
    try:
        kid_from_jwt_header = jwt.get_unverified_header(encoded_token)["kid"]
        for key in ALLOWED_PUBLIC_KEYS.value:
            if key["kid"] == kid_from_jwt_header:
                return key
        raise Unauthorized()
    except InvalidTokenError as error:
        raise Unauthorized() from error
    except KeyError as error:
        raise Unauthorized() from error


def validate_jwt_properties(decoded_jwt: dict) -> None:
    if "exp" not in decoded_jwt:
        raise Unauthorized()
    if "iss" not in decoded_jwt or decoded_jwt["iss"] not in ALLOWED_ISS.value:
        raise Unauthorized()


def decode_jwt(auth_jwt_token: str) -> dict:
    if not AUTH_ENABLED.value:
        raise RuntimeError("AUTH-dedicated features are explicitly disabled!")

    if not (jwk := get_matching_jwk(auth_jwt_token)):
        logger.warning("Failed to find matching jwk.")
        raise Unauthorized()
    for aud in ALLOWED_AUDIENCES.value:
        try:
            public_key = PyJWK(jwk, algorithm="RS256")
            decoded_jwt: dict = jwt.decode(
                auth_jwt_token, public_key.key, algorithms=["RS256"], audience=aud
            )
            validate_jwt_properties(decoded_jwt)
            return decoded_jwt
        except ExpiredSignatureError as error:
            # All the other cases mean the token is malformed/invalid and must be reissued
            raise Unauthorized("Your token has expired. Please refresh it.") from error
        except InvalidAudienceError:
            continue  # Let's try the next audience, maybe it's just not the right one
        except InvalidTokenError as error:
            raise Unauthorized() from error

    raise Unauthorized()


def sign(data: dict, private_key_jwk: dict) -> str:
    """Signs authorization in JWT format."""
    if not isinstance(private_key_jwk, dict):
        raise ValueError("private_key_jwk must be a jwk dict")
    if "kid" not in private_key_jwk:
        raise ValueError("private_key_jwk must have the 'kid' field")
    private_key = PyJWK(private_key_jwk, algorithm="RS256")
    authz: str = jwt.encode(
        data,
        private_key.key,
        algorithm="RS256",
        headers={"kid": private_key_jwk["kid"]},
    )
    return authz
