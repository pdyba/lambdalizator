from unittest.mock import MagicMock, patch

import pytest

from lbz.aws_boto3 import client
from lbz.aws_ssm import SSM


@patch.object(client.ssm, "get_parameter")
def test__get_parameter__returns_value_fetched_from_aws(mocked_get_parameter: MagicMock) -> None:
    mocked_get_parameter.return_value = {"Parameter": {"Value": "x"}}

    value = SSM.get_parameter("param_name")

    assert value == "x"
    mocked_get_parameter.assert_called_once_with(Name="param_name", WithDecryption=True)


@patch.object(client.ssm, "get_parameter")
@pytest.mark.parametrize(
    "expected_error",
    (
        KeyError,
        client.ssm.exceptions.ParameterNotFound(
            {"Error": {"Code": "ParameterNotFound", "Message": "Parameter was not found"}},
            "get_parameter",
        ),
    ),
)
def test__get_parameter__returns_value_none_when_error(
    mocked_get_parameter: MagicMock, expected_error: Exception
) -> None:
    mocked_get_parameter.side_effect = expected_error

    value = SSM.get_parameter("param_name")

    assert value is None
    mocked_get_parameter.assert_called_once_with(Name="param_name", WithDecryption=True)
