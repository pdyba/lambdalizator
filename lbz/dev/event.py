# flake8: noqa
EVENT_TEMPLATE = """
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
