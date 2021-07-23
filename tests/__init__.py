# coding=utf-8
import json
import os
from uuid import uuid4

from tests.fixtures.rsa_pair import (  # noqa:F401
    sample_private_key,
    sample_public_key,
    EXPECTED_TOKEN,
)

os.environ["AUTH_REMOVE_PREFIXES"] = "1"
os.environ["ALLOWED_PUBLIC_KEYS"] = json.dumps({"keys": [sample_public_key]})
os.environ["ALLOWED_AUDIENCES"] = ",".join([str(uuid4()), str(uuid4())])
os.environ["ALLOWED_ISS"] = "test-issuer"
