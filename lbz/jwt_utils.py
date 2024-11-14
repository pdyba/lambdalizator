import jwt
from jwt import PyJWK
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidTokenError

from lbz._cfg import ALLOWED_AUDIENCES, ALLOWED_ISS, ALLOWED_PUBLIC_KEYS
from lbz.exceptions import MissingConfigValue, SecurityError, Unauthorized
from lbz.misc import get_logger

logger = get_logger(__name__)


def get_matching_jwk(encoded_token: str) -> dict:
    """Checks provided JWT token against allowed tokens."""
    try:
        kid_from_jwt_header = jwt.get_unverified_header(encoded_token)["kid"]
        for key in ALLOWED_PUBLIC_KEYS.value:
            if key["kid"] == kid_from_jwt_header:
                return key

        logger.warning(
            "The key with id=%s was not found in the environment variable.",
            kid_from_jwt_header,
        )
        raise Unauthorized
    except InvalidTokenError as error:
        logger.warning("Error finding matching JWK %r", error)
        raise Unauthorized from error
    except KeyError as error:
        logger.warning("The key %s was not found in the JWK.", error.args[0])
        raise Unauthorized from error


def validate_jwt_properties(decoded_jwt: dict) -> None:
    if "exp" not in decoded_jwt:
        raise SecurityError("The auth token doesn't have the 'exp' field.")
    if "iss" not in decoded_jwt:
        raise SecurityError("The auth token doesn't have the 'iss' field.")
    issuer = decoded_jwt["iss"]
    if not issuer or issuer not in ALLOWED_ISS.value:
        raise Unauthorized(f"{issuer} is not an allowed token issuer")


def decode_jwt(auth_jwt_token: str) -> dict:  # noqa:C901
    """Decodes JWT token."""

    if not ALLOWED_PUBLIC_KEYS.value:
        raise MissingConfigValue("ALLOWED_PUBLIC_KEYS")

    if not ALLOWED_AUDIENCES.value:
        raise MissingConfigValue("ALLOWED_AUDIENCES")

    if any("kid" not in public_key for public_key in ALLOWED_PUBLIC_KEYS.value):
        raise RuntimeError("One of the provided public keys doesn't have the 'kid' field")

    if not (jwk := get_matching_jwk(auth_jwt_token)):
        logger.warning("Failed to find matching jwk.")
        raise Unauthorized()
    for idx, aud in enumerate(ALLOWED_AUDIENCES.value, start=1):
        try:
            public_key = PyJWK(jwk, algorithm="RS256")
            decoded_jwt: dict = jwt.decode(
                auth_jwt_token, public_key.key, algorithms=["RS256"], audience=aud
            )
            validate_jwt_properties(decoded_jwt)
            return decoded_jwt
        except InvalidAudienceError as error:
            if idx == len(ALLOWED_AUDIENCES.value):
                logger.warning("Failed decoding JWT with any of JWK - details: %r", error)

                raise Unauthorized() from error
        except ExpiredSignatureError as error:
            raise Unauthorized("Your token has expired. Please refresh it.") from error
        except InvalidTokenError as error:
            logger.warning("Failed decoding JWT with following details: %r", error)
            raise Unauthorized() from error
        except Exception as ex:
            msg = f"An error occurred during decoding the token.\nToken body:\n{auth_jwt_token}"
            raise RuntimeError(msg) from ex
    logger.error("Failed decoding JWT for unknown reason.")
    raise Unauthorized


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
