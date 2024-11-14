from lbz.jwt_utils import sign
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY


def encode_token(claims: dict) -> str:
    return sign(claims, SAMPLE_PRIVATE_KEY)
