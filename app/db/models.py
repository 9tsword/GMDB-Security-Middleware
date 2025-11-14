from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class RoleEnum(str, Enum):
    ADMIN = "system_admin"
    OPERATOR = "operator"
    AUDITOR = "auditor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(SqlEnum(RoleEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("MigrationTask", back_populates="operator")


class SensitiveField(Base):
    __tablename__ = "sensitive_fields"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(String(50), unique=True, nullable=False)
    table_name = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    algorithm_type = Column(String(20), nullable=False)
    status = Column(String(20), default="未加密")
    allow_plain_text_read = Column(Boolean, default=False)
    remarks = Column(Text)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MigrationTaskStatus(str, Enum):
    PENDING = "待启动"
    RUNNING = "进行中"
    COMPLETED = "完成"
    FAILED = "失败"
    PAUSED = "已暂停"
    CANCELLED = "已取消"


class MigrationTask(Base):
    __tablename__ = "migration_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, nullable=False)
    table_name = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    batch_size = Column(Integer, default=1000)
    concurrency = Column(Integer, default=1)
    overwrite_plaintext = Column(Boolean, default=False)
    status = Column(SqlEnum(MigrationTaskStatus), default=MigrationTaskStatus.PENDING)
    progress = Column(Integer, default=0)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    failure_reason = Column(Text)
    operator_id = Column(Integer, ForeignKey("users.id"))

    operator = relationship("User", back_populates="tasks")


class AuditLogType(str, Enum):
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    PROXY = "proxy"
    MIGRATION = "migration"
    KEY_OPERATION = "key_operation"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    log_type = Column(SqlEnum(AuditLogType), nullable=False)
    username = Column(String(50))
    ip_address = Column(String(50))
    table_name = Column(String(100))
    field_name = Column(String(100))
    task_id = Column(String(50))
    operation = Column(String(100))
    status = Column(String(20))
    error_message = Column(Text)
    details = Column(JSON, default=dict)


class SystemConfiguration(Base):
    __tablename__ = "system_configurations"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=False)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))
    notes = Column(Text)
    payload = Column(JSON)


class HelpDocument(Base):
    __tablename__ = "help_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    content = Column(Text)
    attachment_url = Column(String(200))
    version = Column(String(20), default="v1.0.0")
    published_at = Column(DateTime, default=datetime.utcnow)
