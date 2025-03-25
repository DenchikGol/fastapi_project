from enum import Enum


class JWTTokenTypeForLogging(Enum):
    REFRESH = "refresh"
    ACCESS = "access"
