from lbz.lambdas.response import LambdaResponse


class LambdaError(Exception):
    def __init__(self, function_name: str, op: str, result: str, response: LambdaResponse) -> None:
        super().__init__(f"Error response from {function_name} Lambda (op: {op}): {result}")

        self.result = result
        self.response = response
