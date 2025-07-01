import re
from dataclasses import dataclass

from src.shared.exceptions import InvalidUsernameError


@dataclass(frozen=True)
class Username:
    """Имя пользователя - объект-значение."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise InvalidUsernameError("Имя пользователя не может быть пустым")

        # Проверяем длину
        if len(self.value) < 3:
            raise InvalidUsernameError(
                "Имя пользователя должно содержать минимум 3 символа"
            )

        if len(self.value) > 30:
            raise InvalidUsernameError(
                "Имя пользователя не может быть длиннее 30 символов"
            )

        # Проверяем разрешенные символы (буквы, цифры, подчеркивания, дефисы)
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise InvalidUsernameError(
                "Имя пользователя может содержать только буквы, цифры, подчеркивания и дефисы"
            )

        # Не должно начинаться или заканчиваться спецсимволами
        if self.value[0] in "_-" or self.value[-1] in "_-":
            raise InvalidUsernameError(
                "Имя пользователя не может начинаться или заканчиваться подчеркиванием или дефисом"
            )

        # Запрещенные имена
        forbidden_usernames = {
            "admin",
            "administrator",
            "root",
            "api",
            "www",
            "ftp",
            "mail",
            "support",
            "help",
            "info",
            "contact",
            "sales",
            "service",
            "test",
            "demo",
            "guest",
            "anonymous",
            "null",
            "undefined",
        }

        if self.value.lower() in forbidden_usernames:
            raise InvalidUsernameError(
                f"Имя пользователя '{self.value}' зарезервировано"
            )

    def is_valid_format(self) -> bool:
        """Дополнительная проверка формата (может использоваться для UI)."""
        try:
            # Создаем новый объект для проверки
            Username(self.value)
            return True
        except InvalidUsernameError:
            return False

    def __str__(self) -> str:
        return self.value
