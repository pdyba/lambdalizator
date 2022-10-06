from lbz.configuration import ConfigParser, EnvValue

# LBZ configuration
LBZ_DEBUG_MODE = EnvValue("LBZ_DEBUG_MODE", default=False, parser=ConfigParser.env_bool)
LOGGING_LEVEL = EnvValue("LOGGING_LEVEL", default="INFO")
CORS_HEADERS = EnvValue("CORS_HEADERS", default=[], parser=ConfigParser.split_by_comma)
CORS_ORIGIN = EnvValue("CORS_ORIGIN", default=[], parser=ConfigParser.split_by_comma)

# AWS related configuration
AWS_LAMBDA_FUNCTION_NAME = EnvValue("AWS_LAMBDA_FUNCTION_NAME")
EVENTS_BUS_NAME = EnvValue("EVENTS_BUS_NAME")

# Authorization configuration
ALLOWED_PUBLIC_KEYS = EnvValue(
    "ALLOWED_PUBLIC_KEYS", default=[], parser=ConfigParser.load_jwt_keys
)
ALLOWED_AUDIENCES = EnvValue("ALLOWED_AUDIENCES", parser=ConfigParser.split_by_comma)
ALLOWED_ISS = EnvValue("ALLOWED_ISS", default="")
AUTH_REMOVE_PREFIXES = EnvValue(
    "AUTH_REMOVE_PREFIXES", default=bool(0), parser=ConfigParser.env_bool
)
