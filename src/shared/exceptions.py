class DomainError(Exception):
    """Базовое доменное исключение."""
    pass


class DomainValidationError(DomainError):
    """Ошибка валидации в доменном слое."""
    pass


class EntityNotFoundError(DomainError):
    """Сущность не найдена."""
    pass


class BusinessRuleViolationError(DomainError):
    """Нарушение бизнес-правила."""
    pass


# Исключения для авторизации
class AuthenticationError(DomainError):
    """Ошибка аутентификации."""
    pass


class AuthorizationError(DomainError):
    """Ошибка авторизации."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные."""
    pass


class UserAlreadyExistsError(DomainValidationError):
    """Пользователь уже существует."""
    pass


class InvalidTokenError(AuthenticationError):
    """Недействительный токен."""
    pass


class TokenExpiredError(AuthenticationError):
    """Токен истек."""
    pass


class WeakPasswordError(DomainValidationError):
    """Слабый пароль."""
    pass


class InvalidEmailError(DomainValidationError):
    """Некорректный email."""
    pass


class InvalidUsernameError(DomainValidationError):
    """Некорректное имя пользователя."""
    pass


# Исключения для кроссовок (для будущего использования)
class SneakerError(DomainError):
    """Базовая ошибка для кроссовок."""
    pass


class InvalidSKUError(DomainValidationError):
    """Некорректный SKU."""
    pass


class InvalidSizeError(DomainValidationError):
    """Некорректный размер."""
    pass


class InvalidPriceError(DomainValidationError):
    """Некорректная цена."""
    pass


class SneakerNotFoundError(EntityNotFoundError):
    """Кроссовки не найдены."""
    pass


class BrandNotFoundError(EntityNotFoundError):
    """Бренд не найден."""
    pass


class CollectionNotFoundError(EntityNotFoundError):
    """Коллекция не найдена."""
    pass