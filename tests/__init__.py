import os

from tests.fixtures.rsa_pair import (  # noqa:F401
    EXPECTED_TOKEN,
    SAMPLE_PRIVATE_KEY,
    SAMPLE_PUBLIC_KEY,
)

os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
