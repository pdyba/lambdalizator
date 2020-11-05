from typing import Union, List

from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError

from lbz.exceptions import Unauthorized, ServerError
from lbz.misc import get_logger

logger = get_logger(__file__)

STANDARD_CLAIMS = ("sub", "aud", "auth_time", "iss", "exp", "iat", "token_use")


class User:
    def __init__(self, token: str, public_jwk: Union[dict, str], allowed_clients: List[str]):
        self._token = token
        self._public_jwk = public_jwk
        self._allowed_clients = allowed_clients
        for k, v in self.load_cognito_user().items():
            self.__setattr__(k, v)

    def __repr__(self):
        if hasattr(self, "id"):
            return f"User id={self.id}"
        elif hasattr(self, "username"):
            return f"User username={self.username}"

    def load_cognito_user(self) -> dict:
        parsed_user = {}
        attributes = self.decode_cognito_user(self._allowed_clients)
        self._validate_attributes(attributes)
        for k, v in attributes.items():
            if k not in STANDARD_CLAIMS:
                parsed_user[k.replace("cognito:", "").replace("custom:", "")] = v
        return parsed_user

    def decode_cognito_user(self, audiences: list) -> dict:
        try:
            return jwt.decode(
                self._token,
                self._public_jwk,
                algorithms="RS256",
                audience=audiences[0],
            )
        except JWTClaimsError:
            return self.decode_cognito_user(audiences[1:])
        except (JWTError, IndexError):
            raise Unauthorized
        except Exception:
            logger.error(f"Error during decoding, token={self._token}")
            raise ServerError

    @staticmethod
    def _validate_attributes(attributes: dict) -> None:
        if len(attributes) > 1000:
            logger.error(f"Too many attributes, total={len(attributes)}")
            raise RuntimeError


def get_matching_jwk(auth_header: str, cognito_public_keys: dict) -> str:
    try:
        kid = jwt.get_unverified_header(auth_header)["kid"]
        return list(filter(lambda key: key["kid"] == kid, cognito_public_keys)).pop()
    except (JWTError, KeyError):
        raise Unauthorized
    except IndexError:
        logger.error(f"Required key not found in configuration.")
        raise Unauthorized
