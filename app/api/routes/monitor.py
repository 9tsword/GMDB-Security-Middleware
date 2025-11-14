from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.session import get_db
from app.schemas.monitor import MonitorSnapshot, RecentError, ServiceStatus, SystemLoad, KeyStatus

router = APIRouter(prefix="/api/monitor", tags=["monitor"])

SERVICE_START_TIME = datetime.utcnow()


@router.get("/status", response_model=MonitorSnapshot)
def get_status(
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    uptime_seconds = int((now - SERVICE_START_TIME).total_seconds())
    running_tasks = db.query(models.MigrationTask).filter(models.MigrationTask.status == models.MigrationTaskStatus.RUNNING).count()
    total_encryptions = db.query(models.AuditLog).filter(models.AuditLog.log_type == models.AuditLogType.ENCRYPTION).count()
    total_decryptions = db.query(models.AuditLog).filter(models.AuditLog.log_type == models.AuditLogType.DECRYPTION).count()
    total_errors = db.query(models.AuditLog).filter(models.AuditLog.status == "error").count()

    recent_errors = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.status == "error")
        .order_by(models.AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    error_items: List[RecentError] = [
        RecentError(timestamp=log.created_at, message=log.error_message or log.operation or "", severity="error")
        for log in recent_errors
    ]

    config_key_version = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "key_version").first()
    config_valid_until = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "key_valid_until").first()
    config_last_rotation = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "key_last_rotation").first()

    key_version = config_key_version.value if config_key_version else "v1"
    valid_until = (
        datetime.fromisoformat(config_valid_until.value)
        if config_valid_until and config_valid_until.value
        else now.replace(year=now.year + 1)
    )
    last_rotation = (
        datetime.fromisoformat(config_last_rotation.value)
        if config_last_rotation and config_last_rotation.value
        else SERVICE_START_TIME
    )
    is_expired = valid_until < now
    expires_soon = (valid_until - now).days <= 30

    snapshot = MonitorSnapshot(
        service=ServiceStatus(
            service_start_time=SERVICE_START_TIME,
            uptime_seconds=uptime_seconds,
            current_threads=4,
            current_tasks=running_tasks,
            total_encryptions=total_encryptions,
            total_decryptions=total_decryptions,
            total_errors=total_errors,
        ),
        key=KeyStatus(
            version=key_version,
            valid_until=valid_until,
            last_rotation=last_rotation,
            is_expired=is_expired,
            expires_soon=expires_soon,
        ),
        load=SystemLoad(
            cpu_percent=35.5,
            memory_percent=48.2,
            disk_io=120.4,
            db_connections=1,
        ),
        recent_errors=error_items,
    )
    return snapshot
