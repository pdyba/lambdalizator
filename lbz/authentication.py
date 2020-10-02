from typing import Union

from jose import jwt
from jose.exceptions import JWTError

from lbz.exceptions import Unauthorized, ServerError
from lbz.misc import get_logger

logger = get_logger(__file__)


class User:
    def __init__(self, token: str, public_jwk: Union[dict, str], pool_id: str):
        self._token = token
        self._public_jwk = public_jwk
        self._pool_id = pool_id
        for k, v in self.load_cognito_user().items():
            self.__setattr__(k, v)

    def __repr__(self):
        if hasattr(self, "id"):
            return f"User id={self.id}"
        elif hasattr(self, "username"):
            return f"User username={self.username}"

    def load_cognito_user(self) -> dict:
        parsed_user = {}
        attributes = self.decode_cognito_user()
        self._validate_attributes(attributes)
        for k, v in attributes.items():
            parsed_user[k.replace("cognito:", "").replace("custom:", "")] = v
        return parsed_user

    def decode_cognito_user(self) -> dict:
        try:
            return jwt.decode(
                self._token, self._public_jwk, algorithms="RS256", audience=self._pool_id
            )
        except JWTError:
            raise Unauthorized
        except Exception:
            logger.error(f"Error during decoding, token={self._token}")
            raise ServerError

    @staticmethod
    def _validate_attributes(attributes: dict):
        if len(attributes) > 1000:
            logger.error(f"Too many attributes, total={len(attributes)}")
            raise RuntimeError
