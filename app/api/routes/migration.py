from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.models import MigrationTaskStatus
from app.db.session import get_db
from app.schemas import migration as migration_schemas

router = APIRouter(prefix="/api/migration", tags=["migration"])


@router.get("/tasks", response_model=List[migration_schemas.MigrationTaskOut])
def list_tasks(
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    return db.query(models.MigrationTask).all()


@router.post("/tasks", response_model=migration_schemas.MigrationTaskOut)
def create_task(
    payload: migration_schemas.MigrationTaskCreate,
    user: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    if db.query(models.MigrationTask).filter(models.MigrationTask.task_id == payload.task_id).first():
        raise HTTPException(status_code=400, detail="Task already exists")
    task = models.MigrationTask(
        **payload.dict(),
        operator_id=user.id,
        status=MigrationTaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=migration_schemas.MigrationTaskOut)
def get_task(
    task_id: str,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    task = db.query(models.MigrationTask).filter(models.MigrationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _transition_task(task: models.MigrationTask, target_status: MigrationTaskStatus):
    now = datetime.utcnow()
    if target_status == MigrationTaskStatus.RUNNING:
        task.started_at = task.started_at or now
    if target_status in {MigrationTaskStatus.COMPLETED, MigrationTaskStatus.FAILED, MigrationTaskStatus.CANCELLED}:
        task.finished_at = now
    task.status = target_status


@router.post("/tasks/{task_id}/control")
def control_task(
    task_id: str,
    action: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
):
    task = db.query(models.MigrationTask).filter(models.MigrationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if action == "start":
        _transition_task(task, MigrationTaskStatus.RUNNING)
    elif action == "pause":
        _transition_task(task, MigrationTaskStatus.PAUSED)
    elif action == "resume":
        if task.status != MigrationTaskStatus.PAUSED:
            raise HTTPException(status_code=400, detail="Task not paused")
        _transition_task(task, MigrationTaskStatus.RUNNING)
    elif action == "cancel":
        _transition_task(task, MigrationTaskStatus.CANCELLED)
    else:
        raise HTTPException(status_code=400, detail="Unsupported action")
    db.commit()
    db.refresh(task)
    return task


@router.post("/tasks/{task_id}/progress", response_model=migration_schemas.MigrationTaskOut)
def report_progress(
    task_id: str,
    payload: migration_schemas.MigrationTaskUpdate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    task = db.query(models.MigrationTask).filter(models.MigrationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)
    if "status" in data:
        _transition_task(task, data["status"])
    db.commit()
    db.refresh(task)
    return task
