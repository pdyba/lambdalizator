# Change Log

## 0.1.x

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

## 0.2.x

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

## 0.3.x

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

## 0.4.x

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

## 0.5.x

### Version 0.5.0
Released 2021-10-09

- Adds Authorization Inheritance from guest_permissions
- EXPIRATION_KEY is now hardcoded as exp
- Makes iss and exp (previously EXPIRATION_KEY) fields mandatory when authorizing.
- Adds Debug Mode
- Moves All JWT validation to decoding function from resource

### Version 0.5.1
Released 2021-11-17

- Extends CORS capabilities and adds relevant unit tests.

### Version 0.5.2
Released 2022-04-12

- Adds Event Broker to support Asynchronous event handling with AWS Lambda
- Introduces isort for better sorting and related checks
- Updates dependencies

### Version 0.5.3
Released 2022-04-15

- Adds EventApi and EventAware Resource
- Adds Response as a part of Resource, so it can be easily accessed by post hook.
- Improves mypy situation for tests
- Makes Resource's post_request_hook more fault-tolerant

### Version 0.5.4
Released 2022-04-22

- EventApi and EventAware improvements
- Refactors Event to APIGatewayEvent

### Version 0.5.5
Released 2022-06-04

- Fixes EventAPI to send events in chunks (conforms to AWS limits)
- Adds real property methods that protect events list the better way

### Version 0.5.6
Released 2022-07-25

- Adds a decorator that makes the given function an event emitter

### Version 0.5.7
Released 2022-07-26

- Adds optional error codes to exceptions (the LambdaFWException class)

### Version 0.5.8
Released 2022-07-28

- Fixes an issue with permissions overwriting

### Version 0.5.9
Released 2022-07-31

- Starts freezing dependencies with the usage of pip-tools

### Version 0.5.10
Released 2022-07-31

- Logs an error when required ref is missing in the Authorization policy
- Accepts the error_code also during initialization of the Exception

### Version 0.5.11
Released 2022-08-01

- Adds missing exception Too Early - 425

### Version 0.5.12
Released 2022-08-05

- Use the same class representing Event (both sent/received)
- Extends Event Broker with additional, optional parameters
- Adds additional verbose test running to makefile
- Updates dev dependencies

### Version 0.5.13
Released 2022-08-07

- Makes sure that event broker is always passing original event and other handlers cannot affect it.
- Makes DevServer threaded, so it can be run in background, useful for testing

### Version 0.5.14
Released 2022-08-09

- This change contains only library development improvements
- Adds Router cleanup after each test and router fixture
- General tests improvements
- Many mypy related improvements for tests

### Version 0.5.15
Released 2022-08-30

- Adds the all_lbz_errors function

### Version 0.5.16
Released 2022-11-03

- Adds Lambda to Lambda API (client and broker)
- Unifies Event and Lambda APIs
- Adds deprecation wrapper
- Adds Configuration with lazy-loading
- Allows passing context to Resource and stores it within the class
- Adds examples for Event aware API, Event handler (broker), and stand-alone Event producer
- Adds examples for Lambda client and broker. 

### Version 0.5.17
Released 2023-03-10

- Adds Cognito Event Broker
- Adds Cognito generated event enum.

### Version 0.5.18
Released 2023-09-27

- Adjust the behavior of EventAwareResource and event_emitter to clean up EventAPI on its initialization
- Adjust the behavior of EventAPI to always store all events that were processed during one session

### Version 0.5.19
Released 2024-01-02

- Starts verifying the code with the usage of Python 3.9 and Python 3.10
- Adjusts the GitHub Workflow files to make the pipelines more descriptive
- Improves the rest of the repository for upcoming changes

## 0.6.x

### Version 0.6.0
Released 2024-01-05

- Adjusts the code to the latest standards set by Python 3.12
- Disables support for Python 3.8 due to deprecated typing aliases

### Version 0.6.1
Released 2024-01-05

- Extends the code quality tools with security checks

### Version 0.6.2
Released 2024-01-10

- Adds the ability to make an HTTP request bypassing the API Gateway

### Version 0.6.3
Released 2024-01-10

- Cleans the repository after recent pull requests
- Updates the requirements needed for deployment

### Version 0.6.4
Released 2024-01-11

- Allows Lambdalizer to discover packages on its own

### Version 0.6.5
Released 2024-01-31

- Moves `get_response` from exceptions classes to Response class as `from_exception`
- Deprecates `is_ok` method in favour of `ok` property
- Extends Response class to be more useful by adding `json` method
- Migrates away from `datetime.utwnow()` to `datetime.now(UTC)`

### Version 0.6.6
Released 2024-05-24

- Extends `LambdaFWException` with extra property for easier handling edge case exceptions
- Dumps `extra` data into the response when raising an error during handling requests


### Version 0.7.0
Release ETA 2024-02-31 ;)

- Moves REST (API Gateway) related modules into one package
- Moves exceptions to related packages
- Redesigns authorization from ground up
- Adds helpers and reduces jwt-related operations.
- Removes deprecated pre and post requests hooks replaced by pre/post_handle in Resource
- Fixes vulnerability `GHSA-wj6h-64fc-37mp`
