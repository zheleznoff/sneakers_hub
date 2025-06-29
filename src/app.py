from datetime import datetime
from typing import Any, Dict

from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig


# Временные эндпоинты для демонстрации архитектуры
@get("/")
async def root() -> Dict[str, Any]:
    """Корневой эндпоинт - информация о API."""
    return {
        "name": "Sneaker Library API",
        "version": "1.0.0",
        "description": "DDD-архитектура для управления коллекцией кроссовок",
        "endpoints": {
            "sneakers": "/api/sneakers",
            "brands": "/api/brands",
            "collections": "/api/collections",
            "health": "/health",
        },
        "features": [
            "Управление коллекцией кроссовок",
            "Поиск по брендам и моделям",
            "Отслеживание цен и релизов",
            "Личные коллекции пользователей",
        ],
    }


@get("/health")
async def health_check() -> Dict[str, Any]:
    """Проверка состояния сервиса."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "sneaker-library",
    }


def create_app() -> Litestar:
    """Фабрика для создания приложения Litestar."""

    # Конфигурация CORS
    cors_config = CORSConfig(
        allow_origins=["http://localhost:3000", "http://localhost:8080"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Конфигурация OpenAPI
    openapi_config = OpenAPIConfig(
        title="Sneaker Library API",
        version="1.0.0",
        description="DDD-архитектура для управления коллекцией кроссовок",
        contact={"name": "Sneaker Library Team", "email": "api@sneakerlibrary.com"},
        tags=[
            {"name": "Sneakers", "description": "Операции с кроссовками"},
            {"name": "Brands", "description": "Операции с брендами"},
            {"name": "Collections", "description": "Операции с коллекциями"},
            {"name": "Health", "description": "Проверка состояния сервиса"},
        ],
    )

    # Создание приложения
    app = Litestar(
        route_handlers=[root, health_check],
        cors_config=cors_config,
        openapi_config=openapi_config,
        debug=True,  # TODO: Убрать в продакшене
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # TODO: Убрать в продакшене
        log_level="info",
    )
