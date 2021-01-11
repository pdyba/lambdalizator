import os

from lbz.jwt_utils import decode_jwt
from lbz.misc import get_logger

logger = get_logger(__file__)

STANDARD_CLAIMS = ("sub", "aud", "auth_time", "iss", "exp", "iat", "token_use")

REMOVE_PREFIXES = os.environ.get("AUTH_REMOVE_PREFIXES") == "1"


def remove_prefix(text: str):
    return text[text.index(":") + 1 :] if ":" in text else text


class User:
    _max_attributes = 1000

    def __init__(self, token: str):
        self._token = token
        self.username: str = ""
        for k, v in self.get_user_details_from_auth_token().items():
            self.__setattr__(k, v)

    def __repr__(self):
        if hasattr(self, "username"):
            return f"User username={self.username}"

    def get_user_details_from_auth_token(self) -> dict:
        parsed_user = {}
        attributes = decode_jwt(self._token)
        self._validate_attributes(attributes)
        for k, v in attributes.items():
            if k not in STANDARD_CLAIMS:
                parsed_user[remove_prefix(k) if REMOVE_PREFIXES else k] = v
        return parsed_user

    def _validate_attributes(self, attributes: dict) -> None:
        if len(attributes) > self._max_attributes:
            logger.error(
                f"Too many attributes, total={len(attributes)}, limit: {self._max_attributes}"
            )
            raise RuntimeError
