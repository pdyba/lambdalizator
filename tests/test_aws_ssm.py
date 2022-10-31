from unittest.mock import patch

from lbz.aws_boto3 import client
from lbz.aws_ssm import SSM


def test__get_parameter__returns_value_fetched_from_aws() -> None:
    with patch.object(client.ssm, "get_parameter") as mocked_get_parameter:
        mocked_get_parameter.return_value = {"Parameter": {"Value": "x"}}

        value = SSM.get_parameter("param_name")

        assert value == "x"
        mocked_get_parameter.assert_called_once_with(Name="param_name", WithDecryption=True)


def test__get_parameter__returns_value_none_when_unexpected_response() -> None:
    with patch.object(client.ssm, "get_parameter") as mocked_get_parameter:
        mocked_get_parameter.return_value = {}

        value = SSM.get_parameter("param_name")

        assert value is None
        mocked_get_parameter.assert_called_once_with(Name="param_name", WithDecryption=True)


def test__get_parameter__returns_value_none_when_parameter_not_found() -> None:
    with patch.object(client.ssm, "get_parameter") as mocked_get_parameter:
        mocked_get_parameter.side_effect = client.ssm.exceptions.ParameterNotFound(
            {"Error": {"Code": "ParameterNotFound", "Message": "Parameter was not found"}},
            "get_parameter",
        )

        value = SSM.get_parameter("param_name")

        assert value is None
        mocked_get_parameter.assert_called_once_with(Name="param_name", WithDecryption=True)
