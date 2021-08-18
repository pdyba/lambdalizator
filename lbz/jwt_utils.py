# coding=utf-8
"""
JWT helpers module.
"""
import json
import os
from typing import List

from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError, ExpiredSignatureError

from lbz.exceptions import Unauthorized
from lbz.misc import get_logger

logger = get_logger(__name__)

PUBLIC_KEYS: List[dict] = []
ALLOWED_AUDIENCES = []

if allowed_pubkeys_str := os.environ.get("ALLOWED_PUBLIC_KEYS"):
    PUBLIC_KEYS.extend(json.loads(allowed_pubkeys_str)["keys"])
if allowed_audiences_str := os.environ.get("ALLOWED_AUDIENCES"):
    ALLOWED_AUDIENCES.extend(allowed_audiences_str.split(","))

if any("kid" not in public_key for public_key in PUBLIC_KEYS):
    raise ValueError("One of the provided public keys doesn't have the 'kid' field")


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
    except (JWTError, KeyError) as error:
        raise Unauthorized from error


def decode_jwt(auth_jwt_token: str) -> dict:
    """
    Decodes JWT token.
    """
    if not PUBLIC_KEYS:
        msg = "Invalid configuration - no keys in the ALLOWED_PUBLIC_KEYS env variable"
        raise RuntimeError(msg)

    jwk = get_matching_jwk(auth_jwt_token)
    for aud in ALLOWED_AUDIENCES or []:
        try:
            decoded_jwt: dict = jwt.decode(auth_jwt_token, jwk, algorithms="RS256", audience=aud)
            return decoded_jwt
        except JWTClaimsError:
            pass
        except ExpiredSignatureError as error:
            raise Unauthorized("Your token has expired. Please refresh it.") from error
        except JWTError as error:
            raise Unauthorized from error
        except Exception as ex:
            msg = f"An error occurred during decoding the token.\nToken body:\n{auth_jwt_token}"
            raise RuntimeError(msg) from ex

    raise Unauthorized
