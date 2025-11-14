from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.session import get_db
from app.schemas import fields as field_schemas

router = APIRouter(prefix="/api/fields", tags=["fields"])


@router.get("/sensitive", response_model=List[field_schemas.SensitiveFieldOut])
def list_sensitive_fields(
    table_name: Optional[str] = Query(None),
    field_name: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    algorithm_type: Optional[str] = Query(None),
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    query = db.query(models.SensitiveField)
    if table_name:
        query = query.filter(models.SensitiveField.table_name == table_name)
    if field_name:
        query = query.filter(models.SensitiveField.field_name == field_name)
    if status_filter:
        query = query.filter(models.SensitiveField.status == status_filter)
    if algorithm_type:
        query = query.filter(models.SensitiveField.algorithm_type == algorithm_type)
    return query.all()


@router.post("/sensitive", response_model=field_schemas.SensitiveFieldOut)
def create_sensitive_field(
    payload: field_schemas.SensitiveFieldCreate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    if db.query(models.SensitiveField).filter(models.SensitiveField.field_id == payload.field_id).first():
        raise HTTPException(status_code=400, detail="Field already exists")
    field = models.SensitiveField(**payload.dict())
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


@router.put("/sensitive/{field_id}", response_model=field_schemas.SensitiveFieldOut)
def update_sensitive_field(
    field_id: str,
    payload: field_schemas.SensitiveFieldUpdate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    field = db.query(models.SensitiveField).filter(models.SensitiveField.field_id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(field, key, value)
    db.commit()
    db.refresh(field)
    return field


@router.delete("/sensitive/{field_id}")
def delete_sensitive_field(
    field_id: str,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    field = db.query(models.SensitiveField).filter(models.SensitiveField.field_id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    field.is_enabled = False
    db.commit()
    return {"message": "Field disabled"}
