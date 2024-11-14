import jwt

from tests.fixtures.rsa_pair import SAMPLE_PRIVATE_KEY


def encode_token(claims: dict) -> str:
    private_key = jwt.PyJWK(
        SAMPLE_PRIVATE_KEY,
        algorithm="RS256",
    )
    encodeded_jwt: str = jwt.encode(
        claims,
        private_key.key,
        algorithm="RS256",
        headers={"kid": SAMPLE_PRIVATE_KEY["kid"]},
    )
    return encodeded_jwt
