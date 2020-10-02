# Lambdalizator

AWS Lambda REST Toolbox inspired by Flask.
Created and Open Sourced thanks to [LocalBini.com](http://Localbini.com) by @pdyba and @songofroland.


![Python 3.8+](https://img.shields.io/badge/python-v3.8-blue) ![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

## Settings:
For toggling boolean variables, set them to "0" or "1" respectively.
`CLIENT_SECRET` For decoding authorization jwt. Defaults 'secret'.\
`COGNITO_AUTHENTICATION` Toggle authenticating user based on Cognito IdToken. Defaults False.\
`COGNITO_PUBLIC_JWK` For validating signature when Cognito Auth enabled.\
`COGNITO_POOL_ID` Cognito user Pool ID, for validating signature.\
`PRINT_TRACEBACK` More verbose errors. Defaults False.\
`LOGGING_LEVEL` For logging level. Defaults INFO.\

## Hello World Example:
### 1. Define resource
```python 
# simple_resource.py

from lbz.router import add_route
from lbz.communication import Response
from lbz.resource import Resource

class HelloWorld(Resource):

    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})
```
### 2. Define handler
```python
# simple_resource_handler.py

from lbz.exceptions import LambdaFWException

from simple_resource import HelloWorld


def handle(event, context):
    try:
        exp = HelloWorld(event)
        resp = exp()
        return resp
    except Exception as err:
        return LambdaFWException().to_dict()

```
### 3. Create dev Server [Optional]
```python
# simple_resource_dev.py

from lbz.dev.server import MyDevServer

from simple_resource.simple_resource import HelloWorld

if __name__ == '__main__':
    server = MyDevServer(acls=HelloWorld, port=8001)
    server.run()

```

### 4. Unittesting

```python
# python -m unittest simple_resource_test.py
import unittest
from lbz.dev.test import Client

from simple_resource import HelloWorld


class PublicTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client(resource=HelloWorld)

    def test_filter_queries_all_active_when_no_params(self):
        data = self.client.get("/").to_dict()["body"]
        self.assertEqual(data, '{"message":"HelloWorld"}')
```





## Documentation

WIP

## Changelog


[Release Changelogs](./CHANGELOG.md)

Contribution
------------

We are always happy to have new contributions. 
We have marked issues good for anyone looking to get started
Please take a look at our [Contribution guidelines](CONTRIBUTING.md).