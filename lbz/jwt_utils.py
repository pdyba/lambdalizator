"""
JWT helpers module.
"""
import json
from typing import Any

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from lbz.configuration import EnvValue
from lbz.exceptions import SecurityError, Unauthorized
from lbz.misc import get_logger

logger = get_logger(__name__)


PUBLIC_KEYS = EnvValue(
    "ALLOWED_PUBLIC_KEYS", parser=lambda a: json.loads(a)["keys"]
)
ALLOWED_AUDIENCES = EnvValue("ALLOWED_AUDIENCES", parser=lambda a: a.split(","))
ALLOWED_ISS = EnvValue("ALLOWED_ISS", default="")

def public_keys() -> Any:
    keys = PUBLIC_KEYS.value
    if not keys:
        msg = "Invalid configuration - no keys in the ALLOWED_PUBLIC_KEYS env variable"
        raise RuntimeError(msg)
    if any("kid" not in public_key for public_key in keys):
        raise RuntimeError("One of the provided public keys doesn't have the 'kid' field")
    return keys


def allowed_audiences() -> Any:
    if not ALLOWED_AUDIENCES.value:
        raise RuntimeError("ALLOWED_AUDIENCES were not defined")
    return ALLOWED_AUDIENCES.value


def get_matching_jwk(auth_jwt_token: str) -> dict:
    """
    Checks provided JWT token against allowed tokens.
    """
    keys = public_keys()
    try:
        kid_from_jwt_header = jwt.get_unverified_header(auth_jwt_token)["kid"]
        for key in keys:
            if key["kid"] == kid_from_jwt_header:
                return key

        logger.warning(
            "The key with id=%s was not found in the environment variable.", kid_from_jwt_header
        )
        raise Unauthorized
    except JWTError as error:
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
    if not issuer or issuer not in JWTConfig.ALLOWED_ISS.value:
        raise Unauthorized(f"{issuer} is not an allowed token issuer")


def decode_jwt(auth_jwt_token: str) -> dict:  # noqa:C901
    """
    Decodes JWT token.
    """
    jwk = get_matching_jwk(auth_jwt_token)
    audiences = allowed_audiences()
    for idx, aud in enumerate(audiences or [], start=1):
        try:
            decoded_jwt: dict = jwt.decode(auth_jwt_token, jwk, algorithms="RS256", audience=aud)
            validate_jwt_properties(decoded_jwt)
            return decoded_jwt
        except JWTClaimsError as error:
            if idx == len(audiences):
                logger.warning("Failed decoding JWT with any of JWK - details: %r", error)
                raise Unauthorized() from error
        except ExpiredSignatureError as error:
            raise Unauthorized("Your token has expired. Please refresh it.") from error
        except JWTError as error:
            logger.warning("Failed decoding JWT with following details: %r", error)
            raise Unauthorized() from error
        except Exception as ex:
            msg = f"An error occurred during decoding the token.\nToken body:\n{auth_jwt_token}"
            raise RuntimeError(msg) from ex
    logger.error("Failed decoding JWT for unknown reason.")
    raise Unauthorized
