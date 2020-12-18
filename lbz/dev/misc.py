#!/usr/local/bin/python3.8
# coding=utf-8
"""
Dev misc tools.
"""
import json
import pathlib

from uuid import uuid4

WORKING_DIR = pathlib.Path(__file__).parent.absolute()

event = """
{
  "resource": "/",
  "path": "/",
  "httpMethod": "GET",
  "headers": {
    "Content-Type": "application/json",
    "Authentication": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6IioiLCJkZW55Ijp7fX0.piurrcn054AY6MBqlMCAPmEXEb0BlCISRm74EyaOSySJzCE9256vHxFW3SdAhZimEhssaUq-cz5IcaFABNtgzQ",
    "Authorization": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6IioiLCJkZW55Ijp7fX0.piurrcn054AY6MBqlMCAPmEXEb0BlCISRm74EyaOSySJzCE9256vHxFW3SdAhZimEhssaUq-cz5IcaFABNtgzQ"
  },
  "multiValueHeaders": null,
  "queryStringParameters": {},
  "multiValueQueryStringParameters": {},
  "pathParameters": {},
  "stageVariables": null,
  "requestContext": {
    "resourceId": "cszx0g",
    "resourcePath": "/test",
    "httpMethod": "GET",
    "extendedRequestId": "N85eCHnfFiAFjQg=",
    "requestTime": "11/Jun/2020:06:57:55 +0000",
    "path": "/test",
    "accountId": "911122277538",
    "protocol": "HTTP/1.1",
    "stage": "test-invoke-stage",
    "domainPrefix": "testPrefix",
    "requestTimeEpoch": 1591858675351,
    "requestId": "058b41ea-5919-4635-ba8e-96270b2f4a24",
    "identity": {
      "cognitoIdentityPoolId": null,
      "cognitoIdentityId": null,
      "apiKey": "test-invoke-api-key",
      "principalOrgId": null,
      "cognitoAuthenticationType": null,
      "userArn": "arn:aws:iam::911122277538:root",
      "apiKeyId": "test-invoke-api-key-id",
      "userAgent": "aws-internal/3 aws-sdk-java/1.11.783 Linux/4.9.184-0.1.ac.235.83.329.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.252-b09 java/1.8.0_252 vendor/Oracle_Corporation",
      "accountId": "911122277538",
      "caller": "911122277538",
      "sourceIp": "test-invoke-source-ip",
      "accessKey": "ASIA5IIY6USRCKPLZZBL",
      "cognitoAuthenticationProvider": null,
      "user": "911122277538"
    },
    "domainName": "testPrefix.testDomainName",
    "apiId": "2v6hkfr3x0"
  },
  "body": null,
  "isBase64Encoded": false
}
"""


class Event(dict):
    def __init__(
        self,
        resource_path: str,
        method: str,
        body=None,
        query_params=None,
        path_params=None,
        headers=None,
    ):
        """Creates fake Event object."""
        super().__init__(**json.loads(event))

        self["resource"] = resource_path
        self["pathParameters"] = {} if path_params is None else path_params
        self["path"] = resource_path.format(**self.get("pathParameters"))
        self["method"] = method
        self["body"] = {} if body is None else body
        self["headers"] = {"Content-Type": "application/json"} if headers is None else headers
        self["queryStingParameters"] = query_params
        self["multiValueQueryStringParameters"] = query_params
        self["requestContext"]["resourcePath"] = self["resource"]
        self["requestContext"]["path"] = self["path"]
        self["requestContext"]["httpMethod"] = method
        self["requestContext"]["requestId"] = str(uuid4())

    def __repr__(self):
        return f"<Fake Event {self['method']} @ {self['path']} body: {self['body']}>"
