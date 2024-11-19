import jwt
from jwt import PyJWK
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidTokenError
from jwt.types import JWKDict

from lbz._cfg import ALLOWED_AUDIENCES, ALLOWED_ISS, ALLOWED_PUBLIC_KEYS, AUTH_ENABLED
from lbz.exceptions import Unauthorized


def get_matching_public_jwk(token: str) -> JWKDict:
    try:
        token_kid = jwt.get_unverified_header(token)["kid"]
        for public_jwk in ALLOWED_PUBLIC_KEYS.value:
            if public_jwk["kid"] == token_kid:
                return public_jwk
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


def decode_jwt(token: str) -> dict:
    if not AUTH_ENABLED.value:
        raise RuntimeError("AUTH-dedicated features are explicitly disabled!")

    public_jwk = get_matching_public_jwk(token)
    for aud in ALLOWED_AUDIENCES.value:
        try:
            decoded_jwt: dict = jwt.decode(
                jwt=token,
                key=PyJWK(public_jwk, algorithm="RS256").key,
                algorithms=["RS256"],
                audience=aud,
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


def encode_jwt(data: dict, private_jwk: JWKDict) -> str:
    return jwt.encode(
        payload=data,
        key=PyJWK(private_jwk, algorithm="RS256").key,
        algorithm="RS256",
        headers={"kid": private_jwk["kid"]},
    )
