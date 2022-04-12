# coding=utf-8
import json
import os
from uuid import uuid4

from tests.fixtures.rsa_pair import (  # noqa:F401
    EXPECTED_TOKEN,
    SAMPLE_PRIVATE_KEY,
    SAMPLE_PUBLIC_KEY,
)

os.environ["AUTH_REMOVE_PREFIXES"] = "1"
os.environ["ALLOWED_PUBLIC_KEYS"] = json.dumps({"keys": [SAMPLE_PUBLIC_KEY]})
os.environ["ALLOWED_AUDIENCES"] = ",".join([str(uuid4()), str(uuid4())])
os.environ["ALLOWED_ISS"] = "test-issuer"
