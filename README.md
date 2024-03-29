# Lambdalizator

---
[![Stable version](https://img.shields.io/pypi/v/lbz.svg?color=blue)](https://pypi.org/project/lbz/)
[![Python versions](https://img.shields.io/pypi/pyversions/lbz.svg)](https://pypi.org/project/lbz/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1.svg)](https://pycqa.github.io/isort/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org)
[![Downloads](https://pepy.tech/badge/lbz)](https://pepy.tech/project/lbz/)  
_If you want to work with Lambdalizator in Python 3.8, consider using version [0.5.19](https://pypi.org/project/lbz/0.5.19/)._

AWS Lambda Toolbox inspired by Flask. Currently supporting:
- REST API
- Event API (AWS Event Bridge)
- Lambda API



## Authentication

Lambdalizator can automatically read the value of the `Authentication` HTTP header and transform it
into the User object that is available as a part of the request. The `Authentication` header must
contain a JWT token that will be verified using one of the configured public keys (see Configuration
below). The User object will have properties corresponding to the key-value pairs from the token's
data.

To enable authentication provide a value for either `ALLOWED_PUBLIC_KEYS` or `ALLOWED_AUDIENCES`
environment variables.


## Configuration

Lambdalizator can be configured using the following environment variables: 

#### Authorization configuration
- `ALLOWED_PUBLIC_KEYS` - a list of public keys that can be used for decoding auth tokens send in the
  `Authentication` and `Authorization` headers. If you are using Cognito, you can use public keys from:
  https://cognito-idp.{your aws region}.amazonaws.com/{your pool id}/.well-known/jwks.json.
- `ALLOWED_AUDIENCES` - a list of audiences that will be used for verifying the JWTs send in the
  `Authentication` and `Authorization` headers. It should be a comma-separated list of strings,
  e.g. `aud1,aud2`. If not set, any audience will be considered valid.
- `ALLOWED_ISS` - allowed issuer of JWT - Security feature. If not set, issuer will not be checked.
- `AUTH_REMOVE_PREFIXES` - if enabled, all fields starting with a prefix (like `cognito:`) in the
  auth token will have the prefix removed. Defaults to False (set as "0" or "1").

#### Lambdalizator configuration 
- `LOGGING_LEVEL` - log level used in the application. Defaults to INFO.
- `LBZ_DEBUG_MODE` - set lbz to work in debug mode.
- `CORS_HEADERS` - a list of additional headers that should be supported.
- `CORS_ORIGIN` - a list of allowed origins that should be supported.

#### AWS related configuration
- `AWS_LAMBDA_FUNCTION_NAME` - defined by AWS Lambda environment used ATM only in EventAPI
- `EVENTS_BUS_NAME` - expected by EventAPI Event Bridge Events Bus Name. Defaults to Lambda name 
  taken from AWS_LAMBDA_FUNCTION_NAME and extended with `-event-bus`


## Hello World Example:
### 1. Define resource
```python
# simple_resource.py

from lbz.router import add_route
from lbz.response import Response
from lbz.resource import Resource

class HelloWorld(Resource):

    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})
        
```
### 2. Define handler
```python
# simple_resource.py

from lbz.exceptions import LambdaFWException

from simple_resource import HelloWorld


def handle(event, context):
    try:
        return HelloWorld(event)()
    except Exception as err:
        return LambdaFWException().get_response(context.aws_request_id).to_dict()

```
### 3. Create dev Server 🖥️
```python
# simple_resource_dev.py

from lbz.dev.server import MyDevServer

from simple_resource.simple_resource import HelloWorld

if __name__ == '__main__':
    server = MyDevServer(acls=HelloWorld, port=8001)
    server.run()

```

### 4. Don't forget to unit test

```python
# pytest simple_resource_test.py
from lbz.dev.test import Client

from simple_resource import HelloWorld

class TestHelloWorld:
    def setup_method(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.client = Client(resource=HelloWorld)

    def test_filter_queries_all_active_when_no_params(self) -> None:
        data = self.client.get("/").to_dict()["body"]
        assert data == '{"message":"HelloWorld"}'
```

### 5. Authenticate it 💂
```python
# simple_auth/simple_resource.py

from lbz.router import add_route
from lbz.response import Response
from lbz.resource import Resource
from lbz.authz import authorization


class HelloWorld(Resource):
    _name = "helloworld"

    @authorization()
    @add_route("/", method="GET")
    def list(self, restrictions=None):
        return Response({"message": f"Hello, {self.request.user.username} !"})
     
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
