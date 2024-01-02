from lbz.configuration import ConfigParser, EnvValue

# LBZ configuration
LBZ_DEBUG_MODE = EnvValue("LBZ_DEBUG_MODE", default=False, parser=ConfigParser.cast_to_bool)
LOGGING_LEVEL = EnvValue("LOGGING_LEVEL", default="INFO")
CORS_HEADERS = EnvValue[list[str]]("CORS_HEADERS", default=[], parser=ConfigParser.split_by_comma)
CORS_ORIGIN = EnvValue[list[str]]("CORS_ORIGIN", default=[], parser=ConfigParser.split_by_comma)

# AWS related configuration
AWS_LAMBDA_FUNCTION_NAME = EnvValue[str]("AWS_LAMBDA_FUNCTION_NAME")
EVENTS_BUS_NAME = EnvValue[str]("EVENTS_BUS_NAME")

# Authorization configuration
ALLOWED_PUBLIC_KEYS = EnvValue[list[dict]](
    "ALLOWED_PUBLIC_KEYS", default=[], parser=ConfigParser.load_jwt_keys
)
ALLOWED_AUDIENCES = EnvValue("ALLOWED_AUDIENCES", parser=ConfigParser.split_by_comma)
ALLOWED_ISS = EnvValue("ALLOWED_ISS", default="")
AUTH_REMOVE_PREFIXES = EnvValue(
    "AUTH_REMOVE_PREFIXES", default=False, parser=ConfigParser.cast_to_bool
)
