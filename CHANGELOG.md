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
