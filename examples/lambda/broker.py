from lbz.lambdas import LambdaBroker, LambdaResponse, lambda_ok_response
from lbz.types import LambdaContext


def get_user_data(data: dict) -> LambdaResponse:
    print(data)
    return lambda_ok_response()


def send_spam_to_all_users() -> LambdaResponse:
    return lambda_ok_response()


operation_to_handler_map = {
    "get_user_data": get_user_data,
    "send_spam_to_all_users": send_spam_to_all_users,
}


def handle(event: dict, context: LambdaContext) -> LambdaResponse:
    return LambdaBroker(mapper=operation_to_handler_map, event=event, context=context).react()
