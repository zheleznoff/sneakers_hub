import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.domain.entities.user import UserRole, UserStatus

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(254), unique=True, nullable=False, index=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(
        Enum(UserStatus), nullable=False, default=UserStatus.PENDING_VERIFICATION
    )
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, nullable=False, default=0)
    email_verified_at = Column(DateTime, nullable=True)
    is_newsletter_subscribed = Column(Boolean, nullable=False, default=True)

    def __init__(self, **kwargs):
        # Initialize with domain object properties via mapper
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f"UserDB(id={self.id}, username={self.username}, "
            f"email={self.email}, status={self.status.value})"
        )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(32), primary_key=True) 
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    token_hash = Column(String(64), nullable=False) 
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_used_at = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime, nullable=True)

    # Метаданные для безопасности
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True) 
    user_agent = Column(String(500), nullable=True)

    # Связь с пользователем
    user = relationship("User", backref="refresh_tokens")

    def __repr__(self):
        return (
            f"RefreshTokenDB(id={self.id}, user_id={self.user_id}, "
            f"expires_at={self.expires_at}, is_revoked={self.is_revoked})"
        )


__all__ = ["Base", "User", "RefreshToken"]
