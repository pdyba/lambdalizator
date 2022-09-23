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
def test__lambda_source__correctly_recognizes_source_based_on_provided_event(
    source_event: dict, expected_type: str
) -> None:
    assert LambdaSource.get_source(source_event) == expected_type
    assert LambdaSource.is_from(source_event, expected_type)
    assert not LambdaSource.is_from(source_event, "covid")


def test__lambda_source__raises_error_when_event_cannot_be_recognized() -> None:
    event = {"Records": [{"eventSource": "aws:covid"}]}
    with pytest.raises(NotImplementedError, match="Unsupported event type: covid"):
        LambdaSource.get_source(event)
    with pytest.raises(NotImplementedError, match="Unsupported event type: covid"):
        LambdaSource.is_from(event, "covid")
