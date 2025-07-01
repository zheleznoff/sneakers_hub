from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from src.domain.entities.user import UserStatus, UserRole
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(254), unique=True, nullable=False, index=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False) 
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING_VERIFICATION)
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
        return (f"UserDB(id={self.id}, username={self.username}, "
                f"email={self.email}, status={self.status.value})")

__all__ = [
    "Base",
    "User", 
]