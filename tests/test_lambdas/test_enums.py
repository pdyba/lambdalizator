import pytest

from lbz.lambdas import LambdaSource


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
def test_event_types(source_event: dict, expected_type: str) -> None:
    assert LambdaSource.get_source(source_event) == expected_type
    assert LambdaSource.is_from(source_event, expected_type)
    assert not LambdaSource.is_from(source_event, "covid")


def test_event_types_raises_not_implemented() -> None:
    event = {"Records": [{"eventSource": "aws:covid"}]}
    with pytest.raises(NotImplementedError, match="Unsupported event type: covid"):
        assert LambdaSource.get_source(event) == "covid"
    with pytest.raises(NotImplementedError, match="Unsupported event type: covid"):
        assert LambdaSource.is_from(event, "covid")
