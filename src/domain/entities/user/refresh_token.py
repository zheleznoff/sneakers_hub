import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.domain.value_objects.user.user_id import UserId
from src.shared.exceptions import BusinessRuleViolationError, DomainValidationError


@dataclass
class RefreshToken:
    """
    Доменная сущность refresh токена.

    Позволяет пользователю получать новые access токены
    без повторного ввода пароля.
    """

    # Основные атрибуты
    id: str  # Уникальный ID токена
    user_id: UserId
    token_hash: str  # Хеш токена для безопасности

    # Время жизни
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30)
    )
    last_used_at: Optional[datetime] = None

    # Статус
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None

    # Метаданные для безопасности
    device_info: Optional[str] = None  # Краткая информация об устройстве
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def is_valid(self) -> bool:
        """Проверяет, действителен ли токен."""
        return not self.is_revoked and self.expires_at > datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        """Проверяет, истек ли токен."""
        return self.expires_at <= datetime.now(timezone.utc)

    def use(self) -> None:
        """Отмечает использование токена."""
        if not self.is_valid():
            raise BusinessRuleViolationError(
                "Нельзя использовать недействительный токен"
            )

        self.last_used_at = datetime.now(timezone.utc)

    def revoke(self) -> None:
        """Отзывает токен."""
        if self.is_revoked:
            raise BusinessRuleViolationError("Токен уже отозван")

        self.is_revoked = True
        self.revoked_at = datetime.now(timezone.utc)

    def verify_token(self, token: str) -> bool:
        """
        Проверяет соответствие токена.

        Args:
            token: Токен для проверки

        Returns:
            bool: True если токен соответствует
        """
        if not token:
            return False

        token_hash = self._hash_token(token)
        return self.token_hash == token_hash

    def extend_expiry(self, days: int = 30) -> None:
        """
        Продлевает срок действия токена.

        Args:
            days: Количество дней для продления
        """
        if not self.is_valid():
            raise BusinessRuleViolationError("Нельзя продлить недействительный токен")

        if days <= 0 or days > 90:  # Максимум 90 дней
            raise DomainValidationError("Количество дней должно быть от 1 до 90")

        self.expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    def get_remaining_time(self) -> timedelta:
        """Возвращает оставшееся время до истечения."""
        now = datetime.now(timezone.utc)
        if self.expires_at <= now:
            return timedelta(0)
        return self.expires_at - now

    def get_age(self) -> timedelta:
        """Возвращает возраст токена."""
        return datetime.now(timezone.utc) - self.created_at

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Хеширует токен для безопасного хранения.

        Args:
            token: Токен для хеширования

        Returns:
            str: Хеш токена
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _generate_token_id() -> str:
        """
        Генерирует уникальный ID токена.

        Returns:
            str: Уникальный ID
        """
        return secrets.token_urlsafe(16)

    # Фабричные методы

    @classmethod
    def create(
        cls,
        user_id: UserId,
        token: str,
        expires_in_days: int = 30,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "RefreshToken":
        """
        Фабричный метод для создания нового refresh токена.

        Args:
            user_id: ID пользователя
            token: Сам токен
            expires_in_days: Срок действия в днях
            device_info: Информация об устройстве
            ip_address: IP адрес
            user_agent: User-Agent

        Returns:
            RefreshToken: Новый refresh токен
        """
        if expires_in_days <= 0 or expires_in_days > 90:
            raise DomainValidationError("Срок действия должен быть от 1 до 90 дней")

        now = datetime.now(timezone.utc)

        return cls(
            id=cls._generate_token_id(),
            user_id=user_id,
            token_hash=cls._hash_token(token),
            created_at=now,
            expires_at=now + timedelta(days=expires_in_days),
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            is_revoked=False,
        )

    @classmethod
    def create_long_lived(
        cls,
        user_id: UserId,
        token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "RefreshToken":
        """
        Создает долгоживущий refresh токен (для опции "запомнить меня").

        Args:
            user_id: ID пользователя
            token: Сам токен
            device_info: Информация об устройстве
            ip_address: IP адрес
            user_agent: User-Agent

        Returns:
            RefreshToken: Долгоживущий refresh токен (90 дней)
        """
        return cls.create(
            user_id=user_id,
            token=token,
            expires_in_days=90,  # 3 месяца для "запомнить меня"
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def __str__(self) -> str:
        return f"RefreshToken({self.id})"

    def __repr__(self) -> str:
        return (
            f"RefreshToken(id={self.id}, user_id={self.user_id}, "
            f"expires_at={self.expires_at}, is_revoked={self.is_revoked})"
        )
