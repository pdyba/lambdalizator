from typing import Any

from lbz.lambdas import LambdaClient


def get_user_data_from_lambda(user_id: str) -> Any:
    response = LambdaClient.invoke("user-api", "get_user_data", data={"id": user_id})
    return response["data"]


print(get_user_data_from_lambda("AlaMaKota99"))
