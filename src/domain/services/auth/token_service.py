import secrets
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, Optional

from domain.entities.user.refresh_token import RefreshToken
from domain.entities.user.user import User
from domain.value_objects.user.user_id import UserId
from shared.exceptions import InvalidTokenError


class TokenService(ABC):
    """Абстрактный сервис для работы с токенами."""

    @abstractmethod
    def create_access_token(
        self, user: User, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Создает access токен для пользователя.

        Args:
            user: Пользователь
            expires_delta: Время жизни токена

        Returns:
            str: JWT access токен
        """
        pass

    @abstractmethod
    def create_refresh_token(
        self,
        user: User,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False,
    ) -> tuple[str, RefreshToken]:
        """
        Создает refresh токен для пользователя.

        Args:
            user: Пользователь
            device_info: Информация об устройстве
            ip_address: IP адрес
            user_agent: User-Agent
            remember_me: Запомнить пользователя (долгий токен)

        Returns:
            tuple: (сам токен, сущность RefreshToken)
        """
        pass

    @abstractmethod
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Проверяет и декодирует access токен.

        Args:
            token: JWT токен для проверки

        Returns:
            Dict[str, Any]: Данные из токена

        Raises:
            InvalidTokenError: Если токен недействителен
            TokenExpiredError: Если токен истек
        """
        pass

    @abstractmethod
    def refresh_access_token(
        self, refresh_token_value: str, stored_refresh_token: RefreshToken
    ) -> str:
        """
        Обновляет access токен используя refresh токен.

        Args:
            refresh_token_value: Значение refresh токена
            stored_refresh_token: Сущность refresh токена из БД

        Returns:
            str: Новый access токен

        Raises:
            InvalidTokenError: Если refresh токен недействителен
        """
        pass

    def extract_user_id_from_token(self, token: str) -> UserId:
        """
        Извлекает ID пользователя из токена.

        Args:
            token: JWT токен

        Returns:
            UserId: ID пользователя

        Raises:
            InvalidTokenError: Если токен недействителен
        """
        try:
            payload = self.verify_access_token(token)
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise InvalidTokenError("Токен не содержит ID пользователя")

            return UserId.from_string(user_id_str)
        except Exception as e:
            raise InvalidTokenError(f"Ошибка извлечения ID пользователя: {str(e)}")

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Генерирует криптографически стойкий токен.

        Args:
            length: Длина токена в байтах

        Returns:
            str: Безопасный токен
        """
        return secrets.token_urlsafe(length)


class TokenData:
    """Данные для создания токена."""

    def __init__(
        self,
        user_id: UserId,
        username: str,
        email: str,
        role: str,
        is_email_verified: bool = False,
        additional_claims: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.is_email_verified = is_email_verified
        self.additional_claims = additional_claims or {}

    @classmethod
    def from_user(
        cls, user: User, additional_claims: Optional[Dict[str, Any]] = None
    ) -> "TokenData":
        """
        Создает TokenData из сущности User.

        Args:
            user: Сущность пользователя
            additional_claims: Дополнительные claims для токена

        Returns:
            TokenData: Данные для токена
        """
        return cls(
            user_id=user.id,
            username=str(user.username),
            email=str(user.email),
            role=user.role.value,
            is_email_verified=user.is_email_verified,
            additional_claims=additional_claims,
        )

    def to_claims(self) -> Dict[str, Any]:
        """
        Преобразует данные в claims для JWT.

        Returns:
            Dict[str, Any]: Claims для JWT токена
        """
        claims = {
            "sub": str(self.user_id),  # Subject (user ID)
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "email_verified": self.is_email_verified,
            "type": "access",  # Тип токена
        }

        # Добавляем дополнительные claims
        claims.update(self.additional_claims)

        return claims


class AuthTokenPair:
    """Пара токенов для аутентификации."""

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        refresh_token_entity: RefreshToken,
        token_type: str = "Bearer",
        expires_in: int = 3600,  # 1 час по умолчанию
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.refresh_token_entity = refresh_token_entity
        self.token_type = token_type
        self.expires_in = expires_in

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует в словарь для API ответа.

        Returns:
            Dict[str, Any]: Данные токенов для ответа
        """
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_expires_in": int(
                self.refresh_token_entity.get_remaining_time().total_seconds()
            ),
        }


# Константы для токенов
class TokenConstants:
    """Константы для работы с токенами."""

    # Время жизни токенов
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 час
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 дней
    REMEMBER_ME_EXPIRE_DAYS = 90  # 90 дней для "запомнить меня"

    # Типы токенов
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"

    # Claims
    ISSUER = "sneaker-library"
    AUDIENCE = "sneaker-library-users"

    # Алгоритмы
    ALGORITHM = "HS256"

    @classmethod
    def get_access_token_expire_delta(cls) -> timedelta:
        """Возвращает время жизни access токена."""
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

    @classmethod
    def get_refresh_token_expire_delta(cls, remember_me: bool = False) -> timedelta:
        """
        Возвращает время жизни refresh токена.

        Args:
            remember_me: Если True, возвращает долгий срок

        Returns:
            timedelta: Время жизни refresh токена
        """
        days = (
            cls.REMEMBER_ME_EXPIRE_DAYS
            if remember_me
            else cls.REFRESH_TOKEN_EXPIRE_DAYS
        )
        return timedelta(days=days)
