from jose import jwt
from uuid import uuid4
from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY


def encode_token(claims):
    return jwt.encode(
        claims,
        SAMPLE_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": SAMPLE_PRIVATE_KEY["kid"]},
    )

allowed_audiences = [str(uuid4()), str(uuid4())]