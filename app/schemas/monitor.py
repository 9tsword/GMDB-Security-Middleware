from datetime import datetime
from typing import List

from pydantic import BaseModel


class ServiceStatus(BaseModel):
    service_start_time: datetime
    uptime_seconds: int
    current_threads: int
    current_tasks: int
    total_encryptions: int
    total_decryptions: int
    total_errors: int


class KeyStatus(BaseModel):
    version: str
    valid_until: datetime
    last_rotation: datetime
    is_expired: bool
    expires_soon: bool


class SystemLoad(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_io: float
    db_connections: int


class RecentError(BaseModel):
    timestamp: datetime
    message: str
    severity: str


class MonitorSnapshot(BaseModel):
    service: ServiceStatus
    key: KeyStatus
    load: SystemLoad
    recent_errors: List[RecentError]
