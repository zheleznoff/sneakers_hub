import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер базы данных."""

    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def initialize(self) -> None:
        """Инициализирует подключение к базе данных."""

        # Настройки для разных окружений
        engine_kwargs = {
            "echo": settings.database.echo,
            "pool_pre_ping": True,  # Проверка соединения перед использованием
        }

        # Для SQLite используем NullPool
        if "sqlite" in settings.database.url:
            engine_kwargs.update(
                {"poolclass": NullPool, "connect_args": {"check_same_thread": False}}
            )
        else:
            # Для PostgreSQL
            engine_kwargs.update(
                {
                    "pool_size": settings.database.pool_size,
                    "max_overflow": settings.database.max_overflow,
                    "pool_recycle": 3600,  # Пересоздавать соединения каждый час
                    "pool_timeout": 30,  # Таймаут получения соединения
                }
            )

        # Создаем движок
        self.engine = create_async_engine(settings.database.url, **engine_kwargs)

        # Создаем фабрику сессий
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Не очищать объекты после коммита
            autoflush=False,  # Ручное управление flush
            autocommit=False,  # Ручное управление коммитом
        )

        logger.info("Database connection initialized")

    async def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Создает новую сессию базы данных.

        Yields:
            AsyncSession: Сессия базы данных
        """
        if not self.session_factory:
            raise RuntimeError("Database not initialized")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """
        Проверяет доступность базы данных.

        Returns:
            bool: True если база данных доступна
        """
        if not self.engine:
            return False

        try:
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в Litestar.

    Yields:
        AsyncSession: Сессия базы данных
    """
    async for session in db_manager.get_session():
        yield session


async def init_database() -> None:
    """Инициализирует базу данных при старте приложения."""
    db_manager.initialize()
    logger.info("Database initialized")


async def close_database() -> None:
    """Закрывает соединение с базой данных при остановке приложения."""
    await db_manager.close()


# Утилиты для работы с транзакциями


class DatabaseTransaction:
    """Контекстный менеджер для транзакций."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._in_transaction = False

    async def __aenter__(self) -> AsyncSession:
        if not self.session.in_transaction():
            await self.session.begin()
            self._in_transaction = True
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._in_transaction:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()


async def with_transaction(session: AsyncSession) -> DatabaseTransaction:
    """
    Создает контекстный менеджер для транзакции.

    Args:
        session: Сессия базы данных

    Returns:
        DatabaseTransaction: Контекстный менеджер транзакции
    """
    return DatabaseTransaction(session)


# Утилиты для тестирования


async def create_test_database() -> None:
    """Создает тестовую базу данных."""
    # В тестах миграции должны управляться через Alembic
    # Здесь только инициализация подключения
    db_manager.initialize()


async def cleanup_test_database() -> None:
    """Очищает тестовую базу данных."""
    await db_manager.close()


async def reset_test_database() -> None:
    """Сбрасывает тестовую базу данных."""
    # В тестах сброс БД должен происходить через Alembic downgrade/upgrade
    await cleanup_test_database()
    await create_test_database()
