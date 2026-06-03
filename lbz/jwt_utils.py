from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from lbz._cfg import ALLOWED_AUDIENCES, ALLOWED_ISS, ALLOWED_PUBLIC_KEYS, AUTH_ENABLED
from lbz.exceptions import Unauthorized


def get_matching_jwk(auth_jwt_token: str) -> dict:
    try:
        kid_from_jwt_header = jwt.get_unverified_header(auth_jwt_token)["kid"]
        for key in ALLOWED_PUBLIC_KEYS.value:
            if key["kid"] == kid_from_jwt_header:
                return key
        raise Unauthorized()
    except JWTError as error:
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

    jwk = get_matching_jwk(auth_jwt_token)
    for aud in ALLOWED_AUDIENCES.value:
        try:
            decoded_jwt: dict = jwt.decode(auth_jwt_token, jwk, algorithms="RS256", audience=aud)
            validate_jwt_properties(decoded_jwt)
            return decoded_jwt
        except ExpiredSignatureError as error:
            # All the other cases mean the token is malformed/invalid and must be reissued
            raise Unauthorized("Your token has expired. Please refresh it.") from error
        except JWTClaimsError:
            continue  # Let's try the next audience, maybe it's just not the right one
        except JWTError as error:
            raise Unauthorized() from error

    raise Unauthorized()
