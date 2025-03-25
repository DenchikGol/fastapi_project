from pydantic import BaseModel, Field


class Token(BaseModel):
    """Схема для возврата токена."""

    access_token: str = Field(..., description="JWT токен для аутентификации.")
    refresh_token: str = Field(..., description="Токен для обновления access-токена.")
    token_type: str = Field(..., description="Тип токена (обычно 'bearer').")
