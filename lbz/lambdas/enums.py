from typing import Iterable


class LambdaResult:
    ACCEPTED = "ACCEPTED"
    OK = "OK"
    MULTI_STATUS = "MULTI_STATUS"
    # soft errors
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    # hard errors
    CONTRACT_ERROR = "CONTRACT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"

    @classmethod
    def successes(cls) -> Iterable[str]:
        return cls.ACCEPTED, cls.OK, cls.MULTI_STATUS

    @classmethod
    def soft_errors(cls) -> Iterable[str]:
        """Strongly client-dependent errors - in most cases they should be passed on"""
        return cls.BAD_REQUEST, cls.NOT_FOUND, cls.UNAUTHORIZED

    @classmethod
    def hard_errors(cls) -> Iterable[str]:
        """Critical errors affecting communication - except in rare cases, they should be raised"""
        return cls.CONTRACT_ERROR, cls.SERVER_ERROR
