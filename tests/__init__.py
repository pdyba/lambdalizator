# coding=utf-8
import json
import os
from uuid import uuid4

from tests.fixtures.rsa_pair import (  # noqa:F401
    EXPECTED_TOKEN,
    SAMPLE_PRIVATE_KEY,
    SAMPLE_PUBLIC_KEY,
)

# JWT related test config
os.environ["AUTH_REMOVE_PREFIXES"] = "1"
os.environ["ALLOWED_PUBLIC_KEYS"] = json.dumps({"keys": [SAMPLE_PUBLIC_KEY]})
os.environ["ALLOWED_AUDIENCES"] = ",".join([str(uuid4()), str(uuid4())])
os.environ["ALLOWED_ISS"] = "test-issuer"
# AWS related test config
os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "million-dollar-lambda"
os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
