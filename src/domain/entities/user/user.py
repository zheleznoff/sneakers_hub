"""
User Entity - основная сущность пользователя
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from src.domain.value_objects.user.user_id import UserId
from src.domain.value_objects.user.email import Email
from src.domain.value_objects.user.username import Username
from src.domain.value_objects.user.password import Password
from src.shared.exceptions import BusinessRuleViolationError, DomainValidationError


class UserStatus(Enum):
    """Статус пользователя."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserRole(Enum):
    """Роль пользователя."""
    USER = "user"           # Обычный пользователь
    MODERATOR = "moderator" # Модератор
    ADMIN = "admin"         # Администратор


@dataclass
class User:
    """
    Доменная сущность пользователя.
    
    Представляет пользователя системы с его основными атрибутами
    и бизнес-правилами.
    """
    
    # Основные атрибуты
    id: UserId
    email: Email
    username: Username
    password: Password
    
    # Метаданные
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    role: UserRole = UserRole.USER
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Дополнительные поля
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Статистика и настройки
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    email_verified_at: Optional[datetime] = None
    is_newsletter_subscribed: bool = True
    
    def activate(self) -> None:
        """Активирует пользователя."""
        if self.status == UserStatus.ACTIVE:
            raise BusinessRuleViolationError("Пользователь уже активен")
        
        self.status = UserStatus.ACTIVE
        self._mark_as_updated()
    
    def suspend(self, reason: Optional[str] = None) -> None:
        """
        Приостанавливает аккаунт пользователя.
        
        Args:
            reason: Причина приостановки
        """
        if self.status == UserStatus.SUSPENDED:
            raise BusinessRuleViolationError("Пользователь уже приостановлен")
        
        self.status = UserStatus.SUSPENDED
        self._mark_as_updated()
        # TODO: Логирование причины приостановки
    
    def deactivate(self) -> None:
        """Деактивирует пользователя."""
        if self.status == UserStatus.INACTIVE:
            raise BusinessRuleViolationError("Пользователь уже неактивен")
        
        self.status = UserStatus.INACTIVE
        self._mark_as_updated()
    
    def verify_email(self) -> None:
        """Подтверждает email пользователя."""
        if self.email_verified_at is not None:
            raise BusinessRuleViolationError("Email уже подтвержден")
        
        self.email_verified_at = datetime.now(timezone.utc)
        
        # Если пользователь ожидал подтверждения, активируем его
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
        
        self._mark_as_updated()
    
    def change_password(self, new_password: Password) -> None:
        """
        Изменяет пароль пользователя.
        
        Args:
            new_password: Новый пароль
        """
        self.password = new_password
        self._mark_as_updated()
    
    def change_email(self, new_email: Email) -> None:
        """
        Изменяет email пользователя.
        
        Args:
            new_email: Новый email адрес
            
        Raises:
            BusinessRuleViolationError: Если email уже используется или другие ограничения
        """
        if self.email == new_email:
            raise BusinessRuleViolationError("Новый email совпадает с текущим")
        
        self.email = new_email
        # При смене email сбрасываем подтверждение
        self.email_verified_at = None
        self._mark_as_updated()
    
    def change_username(self, new_username: Username) -> None:
        """
        Изменяет имя пользователя.
        
        Args:
            new_username: Новое имя пользователя
            
        Raises:
            BusinessRuleViolationError: Если имя пользователя уже занято
        """
        if self.username == new_username:
            raise BusinessRuleViolationError("Новое имя пользователя совпадает с текущим")
        
        self.username = new_username
        self._mark_as_updated()
    
    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> None:
        """
        Обновляет профиль пользователя.
        
        Args:
            first_name: Имя пользователя
            last_name: Фамилия пользователя
            avatar_url: URL аватара
            
        Raises:
            DomainValidationError: Если данные не прошли валидацию
        """
        if first_name is not None:
            if len(first_name.strip()) > 50:
                raise DomainValidationError("Имя не может быть длиннее 50 символов")
            self.first_name = first_name.strip() or None
        
        if last_name is not None:
            if len(last_name.strip()) > 50:
                raise DomainValidationError("Фамилия не может быть длиннее 50 символов")
            self.last_name = last_name.strip() or None
        
        if avatar_url is not None:
            if avatar_url and len(avatar_url) > 500:
                raise DomainValidationError("URL аватара слишком длинный")
            self.avatar_url = avatar_url or None
        
        self._mark_as_updated()
    
    def record_login(self) -> None:
        """Записывает информацию о входе пользователя."""
        if self.status != UserStatus.ACTIVE:
            raise BusinessRuleViolationError("Пользователь не может войти в систему")
        
        self.last_login_at = datetime.now(timezone.utc)
        self.login_count += 1
        self._mark_as_updated()
    
    def promote_to_moderator(self) -> None:
        """Повышает пользователя до модератора."""
        if self.role == UserRole.ADMIN:
            raise BusinessRuleViolationError("Администратор не может быть понижен до модератора")
        
        if self.status != UserStatus.ACTIVE:
            raise BusinessRuleViolationError("Только активные пользователи могут быть повышены")
        
        self.role = UserRole.MODERATOR
        self._mark_as_updated()
    
    def promote_to_admin(self) -> None:
        """Повышает пользователя до администратора."""
        if self.status != UserStatus.ACTIVE:
            raise BusinessRuleViolationError("Только активные пользователи могут быть повышены")
        
        self.role = UserRole.ADMIN
        self._mark_as_updated()
    
    def demote_to_user(self) -> None:
        """Понижает пользователя до обычного пользователя."""
        if self.role == UserRole.USER:
            raise BusinessRuleViolationError("Пользователь уже имеет базовую роль")
        
        self.role = UserRole.USER
        self._mark_as_updated()
    
    def subscribe_to_newsletter(self) -> None:
        """Подписывает на рассылку."""
        if self.is_newsletter_subscribed:
            raise BusinessRuleViolationError("Пользователь уже подписан на рассылку")
        
        self.is_newsletter_subscribed = True
        self._mark_as_updated()
    
    def unsubscribe_from_newsletter(self) -> None:
        """Отписывает от рассылки."""
        if not self.is_newsletter_subscribed:
            raise BusinessRuleViolationError("Пользователь не подписан на рассылку")
        
        self.is_newsletter_subscribed = False
        self._mark_as_updated()
    
    def verify_password(self, password: str) -> bool:
        """
        Проверяет пароль пользователя.
        
        Args:
            password: Пароль для проверки
            
        Returns:
            bool: True если пароль верный, False иначе
        """
        return self.password.verify(password)
    
    # Вспомогательные методы и свойства
    
    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return str(self.username)
    
    @property
    def is_active(self) -> bool:
        """Проверяет, активен ли пользователь."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_email_verified(self) -> bool:
        """Проверяет, подтвержден ли email."""
        return self.email_verified_at is not None
    
    @property
    def is_admin(self) -> bool:
        """Проверяет, является ли пользователь администратором."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_moderator(self) -> bool:
        """Проверяет, является ли пользователь модератором."""
        return self.role == UserRole.MODERATOR
    
    @property
    def can_moderate(self) -> bool:
        """Проверяет, может ли пользователь модерировать."""
        return self.role in [UserRole.MODERATOR, UserRole.ADMIN]
    
    def _mark_as_updated(self) -> None:
        """Отмечает время последнего обновления."""
        self.updated_at = datetime.now(timezone.utc)
    
    # Фабричные методы
    
    @classmethod
    def create(
        cls,
        email: Email,
        username: Username,
        password: Password,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_id: Optional[UserId] = None
    ) -> 'User':
        """
        Фабричный метод для создания нового пользователя.
        
        Args:
            email: Email адрес
            username: Имя пользователя
            password: Пароль
            first_name: Имя
            last_name: Фамилия
            user_id: ID пользователя (если не указан, генерируется автоматически)
            
        Returns:
            User: Новый пользователь
        """
        now = datetime.now(timezone.utc)
        
        return cls(
            id=user_id or UserId.generate(),
            email=email,
            username=username,
            password=password,
            status=UserStatus.PENDING_VERIFICATION,
            role=UserRole.USER,
            created_at=now,
            updated_at=now,
            first_name=first_name.strip() if first_name else None,
            last_name=last_name.strip() if last_name else None,
            avatar_url=None,
            last_login_at=None,
            login_count=0,
            email_verified_at=None,
            is_newsletter_subscribed=True
        )
    
    @classmethod
    def create_admin(
        cls,
        email: Email,
        username: Username,
        password: Password,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> 'User':
        """
        Фабричный метод для создания администратора.
        
        Args:
            email: Email адрес
            username: Имя пользователя
            password: Пароль
            first_name: Имя
            last_name: Фамилия
            
        Returns:
            User: Новый администратор (сразу активный и с подтвержденным email)
        """
        now = datetime.now(timezone.utc)
        
        admin = cls.create(email, username, password, first_name, last_name)
        admin.role = UserRole.ADMIN
        admin.status = UserStatus.ACTIVE
        admin.email_verified_at = now
        
        return admin
    
    def __str__(self) -> str:
        return f"User({self.username})"
    
    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username}, "
            f"email={self.email}, status={self.status.value})"
        )