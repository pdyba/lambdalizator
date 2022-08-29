from unittest.mock import MagicMock, patch

from lbz.aws_boto3 import client
from lbz.configuration import SSM


@patch.object(client.ssm, "get_parameter")
def test_get_parameter(mocked_get_parameter: MagicMock) -> None:
    mocked_get_parameter.return_value = {"Parameter": {"Value": "x"}}

    value = SSM.get_parameter("path/to/param")

    assert value == "x"
    mocked_get_parameter.assert_called_once_with(Name="path/to/param", WithDecryption=True)
