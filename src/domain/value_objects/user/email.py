import re
from dataclasses import dataclass

from src.shared.exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email:
    """Email адрес пользователя - объект-значение."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise InvalidEmailError("Email не может быть пустым")

        # Проверяем базовый формат email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise InvalidEmailError("Некорректный формат email")

        # Проверяем длину
        if len(self.value) > 254:  # RFC 5321 ограничение
            raise InvalidEmailError("Email слишком длинный (максимум 254 символа)")

        # Проверяем длину локальной части (до @)
        local_part = self.value.split("@")[0]
        if len(local_part) > 64:  # RFC 5321 ограничение
            raise InvalidEmailError(
                "Локальная часть email слишком длинная (максимум 64 символа)"
            )

    @property
    def domain(self) -> str:
        """Возвращает доменную часть email."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Возвращает локальную часть email (до @)."""
        return self.value.split("@")[0]

    def is_business_email(self) -> bool:
        """Проверяет, является ли email корпоративным."""
        personal_domains = {
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "outlook.com",
            "yandex.ru",
            "mail.ru",
            "rambler.ru",
            "icloud.com",
            "yandex.com",
        }
        return self.domain.lower() not in personal_domains

    def __str__(self) -> str:
        return self.value.lower()
