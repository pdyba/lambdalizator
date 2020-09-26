#!/usr/local/bin/python3.8
# coding=utf-8
"""
Dev misc tools.
"""
import json
import pathlib

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
    "resourcePath": "/experiences",
    "httpMethod": "GET",
    "extendedRequestId": "N85eCHnfFiAFjQg=",
    "requestTime": "11/Jun/2020:06:57:55 +0000",
    "path": "/experiences",
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

admin = """
{
  "Authentication": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZCI6InVzci0wYzllMzM4MzRiZTQ0NGY5OTc1M2I2MGQ2N2IxYTA2ZCIsInBlcm1pc3Npb25faWQiOiJyb290In0.nwCADHsVwFztqACjkUW-lg_JywzDEFBK4o4c8MtB9-vdfsumBg4BqVzYuZsxaLugwsll0NtN9oKogDQJKKm96Q",
  "Authorization": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6IioiLCJkZW55Ijp7fX0.piurrcn054AY6MBqlMCAPmEXEb0BlCISRm74EyaOSySJzCE9256vHxFW3SdAhZimEhssaUq-cz5IcaFABNtgzQ"
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
        authorize=False,
        authenticate=False,
    ):
        """Create fake Event object.

        :param body dict
        :param query_params dict
        :param path_params dict
        :param headers dict
        """

        super().__init__(**json.loads(event))
        self.admin = json.loads(admin)

        self["resource"] = resource_path
        self["pathParameters"] = {} if path_params is None else path_params
        self["path"] = resource_path.format(**self.get("pathParameters"))
        self["method"] = method
        self["body"] = {} if body is None else body
        self["headers"] = (
            {"Content-Type": "application/json"} if headers is None else headers
        )
        if authenticate:
            self["headers"]["Authentication"] = self.admin["Authentication"]
        if authorize:
            self["headers"]["Authorization"] = self.admin["Authorization"]
        self["queryStingParameters"] = query_params
        self["multiValueQueryStringParameters"] = query_params
        self["requestContext"]["resourcePath"] = self["resource"]
        self["requestContext"]["path"] = self["path"]
        self["requestContext"]["httpMethod"] = method

    def __repr__(self):
        return f"<Fake Event {self['method']} @ {self['path']} body: {self['body']}>"
