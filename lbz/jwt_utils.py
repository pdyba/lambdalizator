# coding=utf-8
"""
JWT helpers module.
"""
import json
import os
from typing import List

from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError, ExpiredSignatureError

from lbz.exceptions import Unauthorized, SecurityError
from lbz.misc import get_logger

logger = get_logger(__name__)

PUBLIC_KEYS: List[dict] = []
ALLOWED_AUDIENCES = []
ALLOWED_ISS = os.environ.get("ALLOWED_ISS", "")

if allowed_pubkeys_str := os.environ.get("ALLOWED_PUBLIC_KEYS"):
    PUBLIC_KEYS.extend(json.loads(allowed_pubkeys_str)["keys"])
if allowed_audiences_str := os.environ.get("ALLOWED_AUDIENCES"):
    ALLOWED_AUDIENCES.extend(allowed_audiences_str.split(","))

if any("kid" not in public_key for public_key in PUBLIC_KEYS):
    raise RuntimeError("One of the provided public keys doesn't have the 'kid' field")


def get_matching_jwk(auth_jwt_token: str) -> dict:
    """
    Checks provided JWT token against allowed tokens.
    """
    try:
        kid_from_jwt_header = jwt.get_unverified_header(auth_jwt_token)["kid"]
        for key in PUBLIC_KEYS:
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
    if not issuer or issuer not in ALLOWED_ISS:
        raise Unauthorized(f"{issuer} is not an allowed token issuer")


def decode_jwt(auth_jwt_token: str) -> dict:
    """
    Decodes JWT token.
    """
    if not PUBLIC_KEYS:
        msg = "Invalid configuration - no keys in the ALLOWED_PUBLIC_KEYS env variable"
        raise RuntimeError(msg)

    if not ALLOWED_AUDIENCES:
        raise RuntimeError("ALLOWED_AUDIENCES were not defined")

    jwk = get_matching_jwk(auth_jwt_token)
    for idx, aud in enumerate(ALLOWED_AUDIENCES or [], start=1):
        try:
            decoded_jwt: dict = jwt.decode(auth_jwt_token, jwk, algorithms="RS256", audience=aud)
            validate_jwt_properties(decoded_jwt)
            return decoded_jwt
        except JWTClaimsError as error:
            if idx == len(ALLOWED_AUDIENCES):
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
