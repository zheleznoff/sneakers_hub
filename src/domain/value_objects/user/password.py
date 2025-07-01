import re
from dataclasses import dataclass

import bcrypt

from src.shared.exceptions import WeakPasswordError


@dataclass(frozen=True)
class Password:
    """Пароль пользователя - объект-значение."""

    hashed_value: str

    @classmethod
    def from_plain_text(cls, plain_password: str) -> "Password":
        """
        Создает Password из открытого текста с валидацией и хешированием.

        Args:
            plain_password: Пароль в открытом виде

        Returns:
            Password: Объект с хешированным паролем

        Raises:
            WeakPasswordError: Если пароль не соответствует требованиям
        """
        cls._validate_password_strength(plain_password)
        hashed = cls._hash_password(plain_password)
        return cls(hashed_value=hashed)

    @classmethod
    def from_hash(cls, hashed_password: str) -> "Password":
        """
        Создает Password из уже хешированного значения.
        Используется при загрузке из БД.

        Args:
            hashed_password: Уже хешированный пароль

        Returns:
            Password: Объект с хешированным паролем
        """
        if not hashed_password:
            raise WeakPasswordError("Хешированный пароль не может быть пустым")

        return cls(hashed_value=hashed_password)

    def verify(self, plain_password: str) -> bool:
        """
        Проверяет, соответствует ли открытый пароль хешированному.

        Args:
            plain_password: Пароль в открытом виде

        Returns:
            bool: True если пароль верный, False иначе
        """
        if not plain_password:
            return False

        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), self.hashed_value.encode("utf-8")
            )
        except Exception:
            return False

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Валидирует силу пароля.

        Args:
            password: Пароль для проверки

        Raises:
            WeakPasswordError: Если пароль не соответствует требованиям
        """
        if not password:
            raise WeakPasswordError("Пароль не может быть пустым")

        if len(password) < 8:
            raise WeakPasswordError("Пароль должен содержать минимум 8 символов")

        if len(password) > 128:
            raise WeakPasswordError("Пароль не может быть длиннее 128 символов")

        # Проверяем наличие разных типов символов
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        requirements_met = sum([has_lower, has_upper, has_digit, has_special])

        if requirements_met < 3:
            raise WeakPasswordError(
                "Пароль должен содержать минимум 3 типа символов: "
                "строчные буквы, заглавные буквы, цифры, специальные символы"
            )

        # Проверяем на простые пароли
        common_passwords = {
            "password",
            "12345678",
            "qwerty123",
            "admin123",
            "password123",
            "123456789",
            "qwertyuiop",
        }

        if password.lower() in common_passwords:
            raise WeakPasswordError("Пароль слишком простой")

        # Проверяем на повторяющиеся символы
        if len(set(password)) < len(password) * 0.5:
            raise WeakPasswordError(
                "Пароль содержит слишком много повторяющихся символов"
            )

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Хеширует пароль с использованием bcrypt.

        Args:
            password: Пароль в открытом виде

        Returns:
            str: Хешированный пароль
        """
        # Генерируем соль и хешируем пароль
        salt = bcrypt.gensalt(
            rounds=12
        )  # 12 раундов - хороший баланс безопасности/производительности
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def __str__(self) -> str:
        return "***HIDDEN***"  # Никогда не показываем хеш пароля

    def __repr__(self) -> str:
        return "Password(***HIDDEN***)"


def generate_password_requirements() -> dict:
    """
    Возвращает требования к паролю для UI.

    Returns:
        dict: Словарь с требованиями к паролю
    """
    return {
        "min_length": 8,
        "max_length": 128,
        "required_character_types": 3,
        "character_types": [
            "Строчные буквы (a-z)",
            "Заглавные буквы (A-Z)",
            "Цифры (0-9)",
            "Специальные символы (!@#$%^&*...)",
        ],
        "forbidden": [
            "Простые пароли (password, 123456789)",
            "Много повторяющихся символов",
        ],
    }
