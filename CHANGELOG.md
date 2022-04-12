# Change Log


### Version 0.1
Released 2020-09-01

-   First public preview release.

### Version 0.1.3
Released 2020-10-05

-   Added Cognito authentication and user parsing,
-   Security bug fixes.

### Version 0.1.4
Released 2020-10-07

-   Added matching correct JWK based on "kid" parameter in jwt header,

### Version 0.1.6
Released 2020-10-16

-   Refined Cognito authentication configuration,
-   Fixed raising authentication errors,
-   Remove default Cognito claims from User attributes.

### Version 0.1.8
Released 2020-11-03

-   Typing applied,
-   Settings changed to implicitly enable Cognito,
-   Minor improvements.

### Version 0.1.9
Released 2020-11-14

- adds EXPIRATION_KEY config variable for checking authorization expiration.
- adds ALLOWED_ISS config variable setting the allowed JWT issues.

### Version 0.2.0
Released 2020-12-03

- Use RS256 instead of HS512 for signing internal JWT tokens
- Improve authorization module so that it's not coupled with Cognito
- Rename some env variables:
  - `COGNITO_PUBLIC_KEYS` to `ALLOWED_PUBLIC_KEYS`
  - `COGNITO_ALLOWED_CLIENTS` to `ALLOWED_AUDIENCES`
- Remove the `CLIENT_SECRET` env variable to avoid storing secrets in the Lambda configuration
- Add `AUTH_REMOVE_PREFIXES` env variable for controlling whether prefixes (like `cognito:`)
  should be removed from the user data
- Remove the guest authorization feature from the Resource class


### Version 0.2.1
Released 2020-12-15

- Removed implicit wrapping response body to "{message: <body>}" format.
- Added base64 flag to Response instance.
- Improved automatic header resolution.
- Added emojis in Readme.

### Version 0.2.2
Released 2020-12-18

- Headers made case-insensitive dictionary,
- Added version ranges to requirements,
- Added "urn" attribute to Resource,
- Deprecation of authorization and authentication flags in test utility,
- "LambdaFWException" class reworked: added request ID.

### Version 0.3.0
Released 2020-12-18

- Authz module reworked - it's no longer a singleton and it requires using only one decorator

### Version 0.3.1
Released 2020-12-19

- Improvements for the dev server - allow handling of OPTIONS requests, return the right headers
- Fix invoking endpoints without path parameters

### Version 0.3.3
Released 2020-12-29

- Add check_permission function

### Version 0.3.4
Released 2021-01-11

- Add Makefile
- Add mandatory username field in "User" class

### Version 0.3.5
Released 2021-01-16

- Add refs feature to the Authorizer
- Add `log_msg` param to the ServerError class - it can be used to log an error message
  that will not be returned to the user

### Version 0.3.6
Released 2021-03-01

- Add pre_request_hooks and post_request_hooks to the Resource class

### Version 0.3.7
Released 2021-05-25

- Remove the `PRINT_TRACEBACK` setting - it was logging double stack traces
- Add proper handling for server error - return proper error responses
- Don't log errors in case of 4xx responses

### Version 0.3.8
Released 2021-05-27

- Add `has_permission` helper function
- Add common imports to the top level `__init__.py`

### Version 0.3.9
Released 2021-05-28

- Remove common imports from the top level `__init.py`

### Version 0.3.10
Released 2021-06-13

- Improve the messages that are logged in the entire library

### Version 0.3.11
Released 2021-07-08

- Add CORS-enabled Resource class supporting:
  - `*` 
  - `domain.com`
  - `*.domain.com`
- Add Paginated Resource Helper class


### Version 0.3.12
Released 2021-07-18

- Add pylint, with configuration at 10.00/10.00 score


### Version 0.3.13
Released 2021-08-01

- Reworks Exceptions and adds missing ones to be compatible with all HTTP error codes.


### Version 0.3.14
Released 2021-08-10

- Code quality improvements based on mypy type checking


### Version 0.3.15
Released 2021-08-25

- Bug fix for a query params in Paginated Resource


### Version 0.4.0
Released 2021-09-21

- Adds Authorization Collector
- fixes guest policy overwriting proper policy in authz
- improves test runtime
- restores support for dicts in request class


### Version 0.4.1
Released 2021-09-24

- Packaging Type Information \(PEP 561\)



### Version 0.4.2
Released 2021-10-09

- Extends JWT validation cases.
- Adds JWT utils tests.


### Version 0.5.0
Released 2021-10-09

- Adds Authorization Inheritance from guest_permissions
- EXPIRATION_KEY is now hardcoded as exp
- Makes iss and exp (previously EXPIRATION_KEY) fields mandatory when authorizing.
- Adds Debug Mode
- Moves All JWT validation to decoding function from resource



### Version 0.5.2
Released 2022-04-12

- Adds Event Broker to support Asynchronous event handling with AWS Lambda
- Introduces isort for better sorting and related checks
- Updates dependencies