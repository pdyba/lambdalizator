from __future__ import annotations

from lbz.aws_boto3 import client


class SSM:
    @staticmethod
    def get_parameter(name: str) -> str | None:
        try:
            return client.ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
        except (KeyError, client.ssm.exceptions.ParameterNotFound):
            return None
