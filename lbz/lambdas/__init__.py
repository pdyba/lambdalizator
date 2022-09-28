import pytest

from lbz.lambdas.enums import LambdaSource
from tests.exemplary_events import (
    api_gw_event,
    direct_lambda_event,
    dynamodb_event,
    event_bridge_event,
    s3_event,
    sqs_event,
)


@pytest.mark.parametrize(
    "source_event, expected_type",
    (
        (api_gw_event, LambdaSource.API_GW),
        (direct_lambda_event, LambdaSource.DIRECT),
        (dynamodb_event, LambdaSource.DYNAMODB),
        (event_bridge_event, LambdaSource.EVENT_BRIDGE),
        (s3_event, LambdaSource.S3),
        (sqs_event, LambdaSource.SQS),
    ),
)
def test_lambda_source_gives_correct_type_per_full_event(
    source_event: dict, expected_type: str
) -> None:
    assert LambdaSource.get_source(source_event) == expected_type
    assert LambdaSource.is_from(source_event, expected_type)


@pytest.mark.parametrize(
    "source_event, expected_type",
    [
        ({"Records": [{"eventSource": "aws:dynamodb"}]}, LambdaSource.DYNAMODB),
        ({"Records": [{"eventSource": "aws:s3"}]}, LambdaSource.S3),
        ({"Records": [{"eventSource": "aws:sqs"}]}, LambdaSource.SQS),
        ({"httpMethod": "GET"}, LambdaSource.API_GW),
        ({"detail-type": "TESTING"}, LambdaSource.EVENT_BRIDGE),
        ({"invoke_type": "direct_lambda_request"}, LambdaSource.DIRECT),
    ],
)
def test_event_types_minimal(source_event: dict, expected_type: str) -> None:
    assert LambdaSource.get_source(source_event) == expected_type
    assert LambdaSource.is_from(source_event, expected_type)
    assert not LambdaSource.is_from(source_event, "covid")


def test_event_types_raises_not_implemented() -> None:
    event = {"Records": [{"eventSource": "aws:covid"}]}
    with pytest.raises(NotImplementedError, match="Unsupported event type: covid"):
        assert LambdaSource.get_source(event) == "covid"
    with pytest.raises(NotImplementedError, match="Unsupported event type: covid"):
        assert LambdaSource.is_from(event, "covid")
