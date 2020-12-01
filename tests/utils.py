from jose import jwt

from tests.fixtures.rsa_pair import sample_private_key


def encode_token(claims):
    return jwt.encode(
        claims,
        sample_private_key,
        algorithm="RS256",
        headers={'kid': sample_private_key['kid']}
    )
