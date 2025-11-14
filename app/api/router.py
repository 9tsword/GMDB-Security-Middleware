from fastapi import APIRouter

from app.api.routes import auth, backup, configuration, fields, help, logs, migration, monitor, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(fields.router)
api_router.include_router(migration.router)
api_router.include_router(monitor.router)
api_router.include_router(logs.router)
api_router.include_router(configuration.router)
api_router.include_router(backup.router)
api_router.include_router(help.router)
