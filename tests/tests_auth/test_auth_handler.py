from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException, status

from course_web_service.apps.auth_app.handlers import AuthHandler
from course_web_service.core.settings import settings


@pytest.fixture
def auth_handler():
    return AuthHandler()


@pytest.mark.asyncio
async def test_get_password_hash(auth_handler: AuthHandler):
    test_password = "test_password_123"  # noqa: S105

    hashed_password = await auth_handler.get_password_hash(test_password)

    assert hashed_password != test_password
    assert auth_handler.pwd_context.verify(test_password, hashed_password)


@pytest.mark.asyncio
async def test_verify_password(auth_handler: AuthHandler):
    test_password = "test_password_123"  # noqa: S105

    hashed_password = await auth_handler.get_password_hash(test_password)

    assert await auth_handler.verify_password(test_password, hashed_password) is True
    assert await auth_handler.verify_password("wrong_password", hashed_password) is False


@pytest.mark.asyncio
async def test_create_access_token(auth_handler):
    test_data = {"sub": "user_id", "username": "test_user"}

    # 1. Тест с дефолтным expires_delta
    token = await auth_handler.create_access_token(data=test_data)
    decoded_token = jwt.decode(
        token,
        auth_handler.secret,
        algorithms=[auth_handler.algorithm],
    )

    assert decoded_token["sub"] == test_data["sub"]
    assert decoded_token["username"] == test_data["username"]

    expire_timestamp = decoded_token["exp"]
    expire_datetime = datetime.fromtimestamp(expire_timestamp, tz=UTC)
    expected_expire = datetime.now(UTC) + timedelta(
        minutes=settings.auth_settings.access_token_expire_minutes
    )
    assert abs((expire_datetime - expected_expire).total_seconds()) < 1

    # 2. Тест с указанным expires_delta
    custom_expires_delta = timedelta(minutes=30)
    token_custom = await auth_handler.create_access_token(
        data=test_data, expires_delta=custom_expires_delta
    )
    decoded_token_custom = jwt.decode(
        token_custom,
        auth_handler.secret,
        algorithms=[auth_handler.algorithm],
    )

    assert decoded_token_custom["sub"] == test_data["sub"]
    assert decoded_token_custom["username"] == test_data["username"]

    expire_timestamp_custom = decoded_token_custom["exp"]
    expire_datetime_custom = datetime.fromtimestamp(expire_timestamp_custom, tz=UTC)
    expected_expire_custom = datetime.now(UTC) + custom_expires_delta
    assert abs((expire_datetime_custom - expected_expire_custom).total_seconds()) < 1


@pytest.mark.asyncio
async def test_decode_token_success(auth_handler):
    test_data = {"sub": "user_id", "username": "test_user"}
    token = jwt.encode(test_data, auth_handler.secret, algorithm=auth_handler.algorithm)

    payload = await auth_handler.decode_token(token, token_type_for_logger="access")  # noqa: S106

    assert payload["sub"] == test_data["sub"]
    assert payload["username"] == test_data["username"]


@pytest.mark.asyncio
async def test_decode_token_expired(auth_handler):
    """Создаем невалидный токен (с иитекши временем токена)."""
    expired_data = {"sub": "user_id", "exp": 0}  # Время истечения — 1 января 1970 года
    token = jwt.encode(expired_data, auth_handler.secret, algorithm=auth_handler.algorithm)

    # Проверяем, что функция выбрасывает исключение
    with pytest.raises(HTTPException) as exc_info:
        await auth_handler.decode_token(token, token_type_for_logger="access")  # noqa: S106

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Token has expired."


@pytest.mark.asyncio
async def test_decode_token_invalid(auth_handler):
    """Создаем невалидный токен (с неправильным секретом)."""
    invalid_token = jwt.encode({"sub": "user_id"}, "wrong_secret", algorithm=auth_handler.algorithm)

    with pytest.raises(HTTPException) as exc_info:
        await auth_handler.decode_token(invalid_token, token_type_for_logger="access")  # noqa: S106

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token."
