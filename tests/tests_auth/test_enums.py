from course_web_service.apps.auth_app.enums import JWTTokenTypeForLogging


def test_jwt_token_type_for_logging_values():
    """Проверяем, что значения Enum корректны."""
    assert JWTTokenTypeForLogging.REFRESH.value == "refresh"
    assert JWTTokenTypeForLogging.ACCESS.value == "access"


def test_jwt_token_type_for_logging_members():
    """Проверяем, что все члены Enum присутствуют."""
    members = set(JWTTokenTypeForLogging)
    assert members == {JWTTokenTypeForLogging.REFRESH, JWTTokenTypeForLogging.ACCESS}
