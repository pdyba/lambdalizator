import json

from lbz.configuration import EnvValue

# LBZ configuration
LBZ_DEBUG_MODE = EnvValue("LBZ_DEBUG_MODE", default=False, parser=lambda a: a == "true")
LOGGING_LEVEL = EnvValue("LOGGING_LEVEL", default="INFO")
CORS_HEADERS = EnvValue("CORS_HEADERS", default=[], parser=lambda a: a.split(","))
CORS_ORIGIN = EnvValue("CORS_ORIGIN", default=[], parser=lambda a: a.split(","))

# AWS related configuration
AWS_LAMBDA_FUNCTION_NAME = EnvValue("AWS_LAMBDA_FUNCTION_NAME", default="lbz-event-api").value
EVENTS_BUS_NAME = EnvValue(
    "EVENTS_BUS_NAME", default=f"{AWS_LAMBDA_FUNCTION_NAME}-event-bus"
).value

# Authorization configuration
PUBLIC_KEYS = EnvValue("ALLOWED_PUBLIC_KEYS", parser=lambda a: json.loads(a)["keys"])
ALLOWED_AUDIENCES = EnvValue("ALLOWED_AUDIENCES", parser=lambda a: a.split(","))
ALLOWED_ISS = EnvValue("ALLOWED_ISS", default="")
REMOVE_PREFIXES = EnvValue("AUTH_REMOVE_PREFIXES", default=False, parser=bool)
