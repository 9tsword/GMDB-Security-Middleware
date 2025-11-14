from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.db.session import get_db
from app.schemas import configuration as config_schemas

router = APIRouter(prefix="/api/config", tags=["configuration"])


@router.get("", response_model=List[config_schemas.ConfigurationOut])
def list_configurations(
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN, models.RoleEnum.OPERATOR)),
    db: Session = Depends(get_db),
):
    return db.query(models.SystemConfiguration).all()


@router.post("", response_model=config_schemas.ConfigurationOut)
def create_configuration(
    payload: config_schemas.ConfigurationCreate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    if db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == payload.key).first():
        raise HTTPException(status_code=400, detail="Configuration already exists")
    config = models.SystemConfiguration(**payload.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/{config_key}", response_model=config_schemas.ConfigurationOut)
def update_configuration(
    config_key: str,
    payload: config_schemas.ConfigurationUpdate,
    _: models.User = Depends(deps.require_role(models.RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config
