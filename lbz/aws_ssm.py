from typing import Optional

from lbz.aws_boto3 import client


class SSM:
    @staticmethod
    def get_parameter(name: str) -> Optional[str]:
        try:
            return client.ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
        except (KeyError, client.ssm.exceptions.ParameterNotFound):
            return None
