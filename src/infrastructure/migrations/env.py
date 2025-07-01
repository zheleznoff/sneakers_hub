import os
import asyncio
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from alembic import context
from sqlalchemy.engine.base import Connection
from src.infrastructure.persistence.models import Base


load_dotenv()

config = context.config

# Настройка логгирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_database_url() -> str:
    """Получает URL базы данных из переменной окружения."""
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        raise ValueError(
            "DATABASE_URL не найден. Укажите его в .env\n"
            "Пример: postgresql+asyncpg://user:pass@host:port/dbname"
        )
    
    # Автоматическое исправление URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://")
    elif "postgresql://" in db_url and "+asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    print(f"Using database URL: {db_url}")
    return db_url

def run_migrations_offline() -> None:
    """Оффлайн-миграции (для генерации скриптов)."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Асинхронное выполнение миграций."""
    engine = create_async_engine(
        get_database_url(),
        poolclass=NullPool,
        echo=True
    )
    
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await engine.dispose()

def do_run_migrations(connection: Connection) -> None:
    """Основная функция выполнения миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,  # Для лучшей поддержки SQLite при тестировании
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме с asyncpg."""
    try:
        asyncio.run(run_async_migrations())
    except Exception as e:
        print(f"Migration error: {str(e)}")
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()