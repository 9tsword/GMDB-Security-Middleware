from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.session import get_db
from app.schemas import help as help_schemas

router = APIRouter(prefix="/api/help", tags=["help"])


@router.get("", response_model=List[help_schemas.HelpDocumentOut])
def list_help(
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR, models.RoleEnum.AUDITOR)),
    db: Session = Depends(get_db),
):
    return db.query(models.HelpDocument).all()


@router.post("", response_model=help_schemas.HelpDocumentOut)
def create_help(
    payload: help_schemas.HelpDocumentCreate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    doc = models.HelpDocument(**payload.dict())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.put("/{doc_id}", response_model=help_schemas.HelpDocumentOut)
def update_help(
    doc_id: int,
    payload: help_schemas.HelpDocumentUpdate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    doc = db.query(models.HelpDocument).filter(models.HelpDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc
