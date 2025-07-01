import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""

    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def is_sqlite(self) -> bool:
        """Проверяет, используется ли SQLite."""
        return "sqlite" in self.url.lower()

    @property
    def is_postgresql(self) -> bool:
        """Проверяет, используется ли PostgreSQL."""
        return "postgresql" in self.url.lower()


@dataclass
class AuthConfig:
    """Конфигурация аутентификации."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    remember_me_expire_days: int = 90

    def __post_init__(self):
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY должен быть минимум 32 символа")


@dataclass
class APIConfig:
    """Конфигурация API."""

    title: str = "Sneaker Library API"
    version: str = "1.0.0"
    description: str = "DDD-архитектура для управления коллекцией кроссовок"
    debug: bool = False

    # CORS настройки
    cors_origins: list[str] = None
    cors_methods: list[str] = None
    cors_headers: list[str] = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
            ]

        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

        if self.cors_headers is None:
            self.cors_headers = ["*"]


@dataclass
class ServerConfig:
    """Конфигурация сервера."""

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    log_level: str = "info"
    workers: int = 1

    @property
    def is_production(self) -> bool:
        """Проверяет, запущен ли сервер в продакшн режиме."""
        return not self.reload and self.log_level != "debug"


@dataclass
class EmailConfig:
    """Конфигурация email (для будущего использования)."""

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    from_email: Optional[str] = None
    from_name: str = "Sneaker Library"

    @property
    def is_configured(self) -> bool:
        """Проверяет, настроен ли email."""
        return all(
            [self.smtp_host, self.smtp_username, self.smtp_password, self.from_email]
        )


@dataclass
class RedisConfig:
    """Конфигурация Redis (для будущего использования)."""

    url: Optional[str] = None
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0

    @property
    def connection_url(self) -> str:
        """Возвращает URL для подключения к Redis."""
        if self.url:
            return self.url

        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            return f"redis://{self.host}:{self.port}/{self.db}"

    @property
    def is_configured(self) -> bool:
        """Проверяет, настроен ли Redis."""
        return bool(self.url or self.host)


@dataclass
class LoggingConfig:
    """Конфигурация логирования."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    @property
    def use_file_logging(self) -> bool:
        """Проверяет, нужно ли логировать в файл."""
        return bool(self.file_path)


@dataclass
class Settings:
    """Главные настройки приложения."""

    # Основные настройки
    environment: str
    debug: bool

    # Конфигурации модулей
    database: DatabaseConfig
    auth: AuthConfig
    api: APIConfig
    server: ServerConfig
    email: EmailConfig
    redis: RedisConfig
    logging: LoggingConfig

    @classmethod
    def load_from_env(cls) -> "Settings":
        """Загружает настройки из переменных окружения."""

        # Определяем окружение
        environment = os.getenv("ENVIRONMENT", "development")
        debug = (
            environment == "development"
            or os.getenv("DEBUG", "false").lower() == "true"
        )

        # Настройки базы данных
        database_url = os.getenv(
            "DATABASE_URL", "sqlite+aiosqlite:///./sneaker_library.db"
        )

        database_config = DatabaseConfig(
            url=database_url,
            echo=debug and os.getenv("DB_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        )

        # Настройки аутентификации
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            if debug:
                secret_key = (
                    "dev-secret-key-change-in-production-must-be-32-chars-minimum"
                )
            else:
                raise ValueError("SECRET_KEY обязателен в продакшн режиме")

        auth_config = AuthConfig(
            secret_key=secret_key,
            algorithm=os.getenv("ALGORITHM", "HS256"),
            access_token_expire_minutes=int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
            ),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")),
            remember_me_expire_days=int(os.getenv("REMEMBER_ME_EXPIRE_DAYS", "90")),
        )

        # Настройки API
        api_config = APIConfig(
            debug=debug,
            cors_origins=os.getenv("CORS_ORIGINS", "").split(",")
            if os.getenv("CORS_ORIGINS")
            else None,
        )

        # Настройки сервера
        server_config = ServerConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            reload=debug and os.getenv("RELOAD", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "debug" if debug else "info"),
            workers=int(os.getenv("WORKERS", "1")),
        )

        # Настройки email
        email_config = EmailConfig(
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            from_email=os.getenv("FROM_EMAIL"),
            from_name=os.getenv("FROM_NAME", "Sneaker Library"),
        )

        # Настройки Redis
        redis_config = RedisConfig(
            url=os.getenv("REDIS_URL"),
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
        )

        # Настройки логирования
        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),
        )

        return cls(
            environment=environment,
            debug=debug,
            database=database_config,
            auth=auth_config,
            api=api_config,
            server=server_config,
            email=email_config,
            redis=redis_config,
            logging=logging_config,
        )

    @property
    def is_development(self) -> bool:
        """Проверяет, находимся ли мы в режиме разработки."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Проверяет, находимся ли мы в продакшн режиме."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Проверяет, находимся ли мы в тестовом режиме."""
        return self.environment == "testing"


# Создаем глобальный экземпляр настроек
settings = Settings.load_from_env()


# Utility функции
def get_database_url() -> str:
    """Возвращает URL базы данных."""
    return settings.database.url


def get_secret_key() -> str:
    """Возвращает секретный ключ."""
    return settings.auth.secret_key


def is_development() -> bool:
    """Проверяет, находимся ли мы в режиме разработки."""
    return settings.is_development


def is_production() -> bool:
    """Проверяет, находимся ли мы в продакшн режиме."""
    return settings.is_production


def is_testing() -> bool:
    """Проверяет, находимся ли мы в тестовом режиме."""
    return settings.is_testing


# Пути к файлам и папкам
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Возвращаемся к корню проекта
SRC_DIR = PROJECT_ROOT / "src"
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"

# Создаем необходимые папки
LOGS_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
