from jose import jwt
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY


def encode_token(claims) -> str:
    encodeded_jwt: str = jwt.encode(
        claims,
        SAMPLE_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": SAMPLE_PRIVATE_KEY["kid"]},
    )
    return encodeded_jwt
