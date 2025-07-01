"""change id to uuid and make some indexes

Revision ID: 7fa58b06bc13
Revises: 641a36c353b1
Create Date: 2025-07-01 20:04:37.399976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7fa58b06bc13"
down_revision: Union[str, Sequence[str], None] = "641a36c353b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # 1. Включаем расширение uuid-ossp если его нет
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # 2. Проверяем есть ли данные в таблице
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT COUNT(*) FROM users"))
    user_count = result.scalar()
    
    if user_count > 0:
        # Если есть данные - делаем сложную миграцию
        upgrade_with_data()
    else:
        # Если данных нет - простая миграция
        upgrade_empty_table()


def upgrade_with_data() -> None:
    """Upgrade когда в таблице есть данные."""
    
    print("🔄 Обнаружены данные в таблице users, выполняем безопасную миграцию...")
    
    # 1. Добавляем временную колонку с UUID
    op.add_column('users', sa.Column('id_new', postgresql.UUID(), nullable=True))
    
    # 2. Заполняем новыми UUID для существующих записей
    op.execute("UPDATE users SET id_new = uuid_generate_v4()")
    
    # 3. Делаем новую колонку NOT NULL
    op.alter_column('users', 'id_new', nullable=False)
    
    # 4. Удаляем constraints от старой колонки
    op.drop_constraint('users_pkey', 'users', type_='primary')
    
    # 5. Удаляем старую integer колонку
    op.drop_column('users', 'id')
    
    # 6. Переименовываем новую колонку в id
    op.execute('ALTER TABLE users RENAME COLUMN id_new TO id')
    
    # 7. Создаем новый primary key с UUID
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # 8. Обновляем остальные поля и индексы
    apply_other_changes()


def upgrade_empty_table() -> None:
    """Upgrade когда таблица пустая."""
    print("✅ Таблица users пустая, выполняем простую миграцию...")
    
    # Завершаем текущую транзакцию, чтобы избежать ошибок
    op.execute("COMMIT")
    
    try:
        # Удаляем индексы и constraints в отдельных транзакциях
        op.execute("DROP INDEX IF EXISTS ix_users_email")
        op.execute("DROP INDEX IF EXISTS ix_users_username")
        
        # Удаляем таблицу в отдельной транзакции
        op.execute("DROP TABLE IF EXISTS users CASCADE")
        
        # Начинаем новую транзакцию для создания таблицы
        op.execute("BEGIN")
        
        # Создаем таблицу заново с UUID
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('email', sa.String(length=254), nullable=False),
            sa.Column('username', sa.String(length=30), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('status', postgresql.ENUM(
                'ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION',
                name='userstatus', create_type=False), nullable=False),
            sa.Column('role', postgresql.ENUM(
                'USER', 'MODERATOR', 'ADMIN', 
                name='userrole', create_type=False), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('first_name', sa.String(length=50), nullable=True),
            sa.Column('last_name', sa.String(length=50), nullable=True),
            sa.Column('avatar_url', sa.String(length=500), nullable=True),
            sa.Column('bio', sa.String(length=500), nullable=True),
            sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('is_newsletter_subscribed', sa.Boolean(), nullable=False, server_default='true'),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Создаем индексы
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
        op.create_index('ix_users_username', 'users', ['username'], unique=True)
        op.create_index('ix_users_email_status', 'users', ['email', 'status'])
        op.create_index('ix_users_created_at', 'users', ['created_at'])
        
    except Exception as e:
        op.execute("ROLLBACK")
        raise e


def apply_other_changes() -> None:
    """Применяет остальные изменения к таблице."""
    
    with op.batch_alter_table("users", schema=None) as batch_op:
        # Изменяем длину полей
        batch_op.alter_column(
            "email",
            existing_type=sa.VARCHAR(length=255),
            type_=sa.String(length=254),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "username",
            existing_type=sa.VARCHAR(length=50),
            type_=sa.String(length=30),
            existing_nullable=False,
        )
        
        # Удаляем старые индексы если они есть
        try:
            batch_op.drop_index("ix_users_email")
        except:
            pass
        
        try:
            batch_op.drop_index("ix_users_username")
        except:
            pass
            
        try:
            batch_op.drop_index("ix_users_email_status")
        except:
            pass
            
        try:
            batch_op.drop_index("ix_users_created_at")
        except:
            pass
        
        # Удаляем старые constraints если они есть
        try:
            batch_op.drop_constraint("users_email_key", type_="unique")
        except:
            pass
        
        try:
            batch_op.drop_constraint("users_username_key", type_="unique")
        except:
            pass
        
        # Создаем новые индексы
        batch_op.create_index('ix_users_email', ["email"], unique=True)
        batch_op.create_index('ix_users_username', ["username"], unique=True)
        batch_op.create_index('ix_users_email_status', ['email', 'status'])
        batch_op.create_index('ix_users_created_at', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    
    print("⚠️  ВНИМАНИЕ: Downgrade приведет к потере UUID данных!")
    print("UUID будут заменены на автоинкрементные INTEGER ID")
    
    # Удаляем индексы перед работой с таблицей
    try:
        op.drop_index('ix_users_email', 'users')
        op.drop_index('ix_users_username', 'users')
        op.drop_index('ix_users_email_status', 'users')
        op.drop_index('ix_users_created_at', 'users')
    except:
        pass
    
    # 1. Создаем временную таблицу с INTEGER ID
    op.execute('''
        CREATE TABLE users_temp (
            id SERIAL PRIMARY KEY,
            email VARCHAR(254) NOT NULL,
            username VARCHAR(30) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            status userstatus NOT NULL,
            role userrole NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
            last_login_at TIMESTAMP WITH TIME ZONE,
            email_verified_at TIMESTAMP WITH TIME ZONE,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            avatar_url VARCHAR(500),
            bio VARCHAR(500),
            login_count INTEGER NOT NULL DEFAULT 0,
            is_newsletter_subscribed BOOLEAN NOT NULL DEFAULT true
        )
    ''')
    
    # 2. Копируем данные (UUID будут потеряны, ID станут автоинкрементными)
    op.execute('''
        INSERT INTO users_temp (
            email, username, password_hash, status, role,
            created_at, updated_at, last_login_at, email_verified_at,
            first_name, last_name, avatar_url, bio,
            login_count, is_newsletter_subscribed
        )
        SELECT 
            email, username, password_hash, status, role,
            created_at, updated_at, last_login_at, email_verified_at,
            first_name, last_name, avatar_url, bio,
            login_count, is_newsletter_subscribed
        FROM users
        ORDER BY created_at  -- Сортируем для предсказуемого порядка ID
    ''')
    
    # 3. Удаляем таблицу с UUID
    op.drop_table('users')
    
    # 4. Переименовываем временную таблицу
    op.execute('ALTER TABLE users_temp RENAME TO users')
    
    # 5. Создаем старые constraints и индексы
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)