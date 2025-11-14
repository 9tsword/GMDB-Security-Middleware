from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.session import get_db
from app.schemas import backup as backup_schemas

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.post("", response_model=backup_schemas.BackupRecordOut)
def create_backup(
    payload: backup_schemas.BackupRecordCreate,
    user: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    record = models.BackupRecord(
        created_by=user.username,
        notes=payload.notes,
        payload=payload.payload,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[backup_schemas.BackupRecordOut])
def list_backups(
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    return db.query(models.BackupRecord).order_by(models.BackupRecord.created_at.desc()).all()
