from dataclasses import dataclass
from uuid import UUID, uuid4
from src.shared.exceptions import DomainValidationError


@dataclass(frozen=True)
class UserId:
    """Идентификатор пользователя - объект-значение."""

    value: UUID

    @classmethod
    def generate(cls) -> "UserId":
        """
        Генерирует новый уникальный ID пользователя.

        Returns:
            UserId: Новый идентификатор пользователя
        """
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "UserId":
        """
        Создает UserId из строкового представления.

        Args:
            id_str: Строковое представление UUID

        Returns:
            UserId: Идентификатор пользователя

        Raises:
            DomainValidationError: Если строка не является валидным UUID
        """
        try:
            return cls(UUID(id_str))
        except ValueError as e:
            raise DomainValidationError(f"Некорректный формат User ID: {id_str}") from e

    @classmethod
    def from_uuid(cls, uuid_value: UUID) -> "UserId":
        """
        Создает UserId из UUID объекта.

        Args:
            uuid_value: UUID объект

        Returns:
            UserId: Идентификатор пользователя
        """
        return cls(uuid_value)

    def to_string(self) -> str:
        """
        Возвращает строковое представление ID.

        Returns:
            str: Строковое представление UUID
        """
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, UserId):
            return False
        return self.value == other.value
