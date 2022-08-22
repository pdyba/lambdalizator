from typing import Any

from lbz.aws_boto3 import client


class SSM:
    @staticmethod
    def get_parameter(name: str) -> Any:
        return client.ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
