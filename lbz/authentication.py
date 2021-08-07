# coding=utf-8
"""
JWT based Authentication module.
"""
import os

from lbz.jwt_utils import decode_jwt

STANDARD_CLAIMS = ("sub", "aud", "auth_time", "iss", "exp", "iat", "token_use")

REMOVE_PREFIXES = os.environ.get("AUTH_REMOVE_PREFIXES") == "1"


def remove_prefix(text: str) -> str:
    """
    Removes prefix of a text based on : sign.
    """
    return text.split(":", maxsplit=1)[1] if ":" in text else text


class User:
    _max_attributes = 1000

    def __init__(self, token: str):
        self._token = token
        self.username: str = ""
        for key, value in self.get_user_details_from_auth_token().items():
            self.__setattr__(key, value)

    def __repr__(self) -> str:
        if hasattr(self, "username"):
            return f"User username={self.username}"
        return "User"

    def get_user_details_from_auth_token(self) -> dict:
        """
        Parses auth token for user details.
        """
        parsed_user = {}
        attributes = decode_jwt(self._token)
        self._validate_attributes(attributes)
        for key, value in attributes.items():
            if key not in STANDARD_CLAIMS:
                parsed_user[remove_prefix(key) if REMOVE_PREFIXES else key] = value
        return parsed_user

    def _validate_attributes(self, attributes: dict) -> None:
        if (total_attributes := len(attributes)) > self._max_attributes:
            msg = f"Too many attributes, total={total_attributes}, limit={self._max_attributes}"
            raise RuntimeError(msg)
