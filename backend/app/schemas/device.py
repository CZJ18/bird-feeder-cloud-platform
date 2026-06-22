from __future__ import annotations

from pydantic import BaseModel, Field


class DeviceConfigIn(BaseModel):
    capture_interval: int = Field(default=300, ge=1)
    confidence_threshold: float = Field(default=0.85, ge=0, le=1)
    upload_image: bool = True
    night_mode: bool = True
    low_battery_threshold: int = Field(default=20, ge=0, le=100)


class DeviceCommandIn(BaseModel):
    device_id: str
    command: str
