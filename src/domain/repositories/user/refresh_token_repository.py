from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from domain.entities.user.refresh_token import RefreshToken
from domain.value_objects.user.user_id import UserId


class RefreshTokenRepository(ABC):
    """Абстрактный репозиторий для работы с refresh токенами."""

    @abstractmethod
    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        """
        Сохраняет refresh токен.

        Args:
            refresh_token: Токен для сохранения

        Returns:
            RefreshToken: Сохраненный токен
        """
        pass

    @abstractmethod
    async def get_by_id(self, token_id: str) -> Optional[RefreshToken]:
        """
        Получает refresh токен по ID.

        Args:
            token_id: ID токена

        Returns:
            Optional[RefreshToken]: Токен или None если не найден
        """
        pass

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """
        Получает refresh токен по хешу.

        Args:
            token_hash: Хеш токена

        Returns:
            Optional[RefreshToken]: Токен или None если не найден
        """
        pass

    @abstractmethod
    async def get_user_tokens(
        self, user_id: UserId, only_valid: bool = True
    ) -> List[RefreshToken]:
        """
        Получает все refresh токены пользователя.

        Args:
            user_id: ID пользователя
            only_valid: Только действительные токены

        Returns:
            List[RefreshToken]: Список токенов пользователя
        """
        pass

    @abstractmethod
    async def revoke_token(self, token_id: str) -> bool:
        """
        Отзывает refresh токен.

        Args:
            token_id: ID токена для отзыва

        Returns:
            bool: True если токен был отозван, False если не найден
        """
        pass

    @abstractmethod
    async def revoke_user_tokens(
        self, user_id: UserId, except_token_id: Optional[str] = None
    ) -> int:
        """
        Отзывает все refresh токены пользователя.

        Args:
            user_id: ID пользователя
            except_token_id: ID токена, который НЕ нужно отзывать

        Returns:
            int: Количество отозванных токенов
        """
        pass

    @abstractmethod
    async def delete_expired_tokens(
        self, before_date: Optional[datetime] = None
    ) -> int:
        """
        Удаляет истекшие токены.

        Args:
            before_date: Удалить токены истекшие до этой даты
                        (по умолчанию - текущее время)

        Returns:
            int: Количество удаленных токенов
        """
        pass

    @abstractmethod
    async def delete_revoked_tokens(
        self, before_date: Optional[datetime] = None
    ) -> int:
        """
        Удаляет отозванные токены старше указанной даты.

        Args:
            before_date: Удалить отозванные токены старше этой даты

        Returns:
            int: Количество удаленных токенов
        """
        pass

    @abstractmethod
    async def count_user_tokens(self, user_id: UserId, only_valid: bool = True) -> int:
        """
        Подсчитывает количество токенов пользователя.

        Args:
            user_id: ID пользователя
            only_valid: Только действительные токены

        Returns:
            int: Количество токенов
        """
        pass

    @abstractmethod
    async def get_tokens_by_device(
        self, user_id: UserId, device_info: str
    ) -> List[RefreshToken]:
        """
        Получает токены пользователя для конкретного устройства.

        Args:
            user_id: ID пользователя
            device_info: Информация об устройстве

        Returns:
            List[RefreshToken]: Токены для устройства
        """
        pass

    @abstractmethod
    async def cleanup_old_tokens(self, older_than_days: int = 90) -> int:
        """
        Очищает старые токены (как истекшие, так и отозванные).

        Args:
            older_than_days: Удалить токены старше указанного количества дней

        Returns:
            int: Количество удаленных токенов
        """
        pass
