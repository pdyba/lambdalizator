from typing import Type

from lbz.dev.misc import APIGatewayEvent
from lbz.lambdas import LambdaBroker, LambdaClient, LambdaResponse, LambdaResult
from lbz.misc import get_logger
from lbz.resource import Resource
from lbz.response import Response
from lbz.type_defs import LambdaContext

logger = get_logger(__name__)

REST_OVER_LAMBDA_OP = "REST_OVER_LAMBDA_OP"


class RestOverLambdaBroker(LambdaBroker):
    def __init__(self, event: dict, context: LambdaContext, resource: Type[Resource]):
        super().__init__(event=event, context=context, mapper={REST_OVER_LAMBDA_OP: self.process})
        self.resource = resource

    def process(self, data: dict) -> LambdaResponse:
        response = self._process(**data)

        return LambdaResponse(
            result=LambdaResult.OK if response.status_code < 400 else LambdaResult.SERVER_ERROR,
            data=response.body,
        )

    def _process(
        self,
        path: str,
        method: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> Response:
        if query_params:
            for key, value in query_params.items():
                if not isinstance(value, list):
                    query_params[key] = [str(value)]
                else:
                    query_params[key] = [str(elem) for elem in value]
        return self.resource(
            APIGatewayEvent(
                resource_path=path,
                method=method,
                body=body,
                path_params=params,
                query_params=query_params,
                headers=headers,
            )
        )()


class RestOverLambdaClient(LambdaClient):
    def __init__(self, function_name: str):
        self.function_name = function_name

    def request(
        self,
        path: str,
        method: str,
        params: dict = None,
        query_params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> LambdaResponse:
        data = {
            "path": path,
            "method": method,
            "params": params,
            "query_params": query_params,
            "body": body,
            "headers": headers,
        }
        return self.invoke(self.function_name, op=REST_OVER_LAMBDA_OP, data=data)
