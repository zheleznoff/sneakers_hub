from dataclasses import dataclass
from typing import Optional

from domain.value_objects.user.user_id import UserId


@dataclass
class RegisterUserCommand:
    """Команда регистрации нового пользователя."""

    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Метаданные запроса
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None


@dataclass
class LoginUserCommand:
    """Команда входа пользователя в систему."""

    email_or_username: str  # Можно войти по email или username
    password: str
    remember_me: bool = False

    # Метаданные запроса
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None


@dataclass
class RefreshTokenCommand:
    """Команда обновления access токена."""

    refresh_token: str

    # Метаданные запроса (для валидации)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class LogoutUserCommand:
    """Команда выхода пользователя."""

    refresh_token: str
    logout_all_devices: bool = False


@dataclass
class RevokeTokenCommand:
    """Команда отзыва конкретного токена."""

    user_id: UserId
    token_id: str


@dataclass
class RevokeAllUserTokensCommand:
    """Команда отзыва всех токенов пользователя."""

    user_id: UserId
    except_current_token: Optional[str] = None  # Не отзывать текущий токен


@dataclass
class ChangePasswordCommand:
    """Команда смены пароля."""

    user_id: UserId
    current_password: str
    new_password: str
    logout_all_devices: bool = True  # По умолчанию выходим со всех устройств


@dataclass
class ResetPasswordCommand:
    """Команда сброса пароля."""

    email: str

    # Метаданные запроса
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class ConfirmPasswordResetCommand:
    """Команда подтверждения сброса пароля."""

    reset_token: str
    new_password: str

    # Метаданные запроса
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class VerifyEmailCommand:
    """Команда подтверждения email."""

    verification_token: str

    # Метаданные запроса
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class ResendEmailVerificationCommand:
    """Команда повторной отправки письма с подтверждением."""

    email: str

    # Метаданные запроса
    ip_address: Optional[str] = None


@dataclass
class UpdateProfileCommand:
    """Команда обновления профиля пользователя."""

    user_id: UserId
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class ChangeEmailCommand:
    """Команда смены email адреса."""

    user_id: UserId
    new_email: str
    password: str  # Подтверждение паролем

    # Метаданные запроса
    ip_address: Optional[str] = None


@dataclass
class ChangeUsernameCommand:
    """Команда смены имени пользователя."""

    user_id: UserId
    new_username: str
    password: str  # Подтверждение паролем


# Результаты команд


@dataclass
class AuthTokenResult:
    """Результат команд аутентификации с токенами."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_expires_in: int = 2592000  # 30 дней


@dataclass
class UserRegistrationResult:
    """Результат регистрации пользователя."""

    user_id: UserId
    email: str
    username: str
    email_verification_required: bool = True
    tokens: Optional[AuthTokenResult] = None  # Если сразу авторизуем


@dataclass
class LoginResult:
    """Результат входа пользователя."""

    user_id: UserId
    email: str
    username: str
    tokens: AuthTokenResult
    is_email_verified: bool
    last_login_at: Optional[str] = None


@dataclass
class RefreshTokenResult:
    """Результат обновления токена."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


@dataclass
class PasswordResetResult:
    """Результат запроса сброса пароля."""

    email: str
    reset_token_sent: bool = True
    expires_in_minutes: int = 15


@dataclass
class EmailVerificationResult:
    """Результат подтверждения email."""

    user_id: UserId
    email: str
    verified_at: str
    auto_login: bool = False
    tokens: Optional[AuthTokenResult] = None


@dataclass
class ProfileUpdateResult:
    """Результат обновления профиля."""

    user_id: UserId
    updated_fields: list[str]
    updated_at: str
