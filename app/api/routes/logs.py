import csv
import io
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.session import get_db
from app.schemas import logs as log_schemas

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=List[log_schemas.AuditLogOut])
def list_logs(
    log_type: Optional[models.AuditLogType] = Query(None),
    user: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    field_name: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    query = db.query(models.AuditLog)
    if log_type:
        query = query.filter(models.AuditLog.log_type == log_type)
    if user:
        query = query.filter(models.AuditLog.username == user)
    if table_name:
        query = query.filter(models.AuditLog.table_name == table_name)
    if field_name:
        query = query.filter(models.AuditLog.field_name == field_name)
    if task_id:
        query = query.filter(models.AuditLog.task_id == task_id)
    return query.order_by(models.AuditLog.created_at.desc()).limit(200).all()


@router.post("", response_model=log_schemas.AuditLogOut)
def create_log(
    payload: log_schemas.AuditLogCreate,
    user: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    log = models.AuditLog(**payload.dict())
    log.username = log.username or user.username
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/export")
def export_logs(
    format: str = Query("csv"),
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    logs = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(1000).all()
    if format not in {"csv", "excel"}:
        raise HTTPException(status_code=400, detail="Unsupported format")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["时间", "用户", "类型", "表名", "字段名", "任务", "操作", "状态", "错误信息"])
    for log in logs:
        writer.writerow([
            log.created_at.isoformat(),
            log.username,
            log.log_type.value,
            log.table_name,
            log.field_name,
            log.task_id,
            log.operation,
            log.status,
            log.error_message,
        ])
    output.seek(0)
    media_type = "text/csv"
    filename = "audit_logs.csv" if format == "csv" else "audit_logs.xlsx"
    return StreamingResponse(output, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
