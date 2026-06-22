from __future__ import annotations

import secrets
from datetime import datetime

from app.config import settings
from app.models import Device, DeviceStatus
from app.utils.time_utils import recent_threshold


async def get_or_create_device(device_id: str, name: str | None = None) -> Device:
    device = await Device.get_or_none(device_id=device_id)
    if device:
        return device
    return await Device.create(
        device_id=device_id,
        name=name or device_id,
        api_key=secrets.token_hex(32),
        status=1,
    )


async def latest_status(device: Device) -> DeviceStatus | None:
    return await DeviceStatus.filter(device=device).order_by("-timestamp").first()


def is_online(status: DeviceStatus | None) -> bool:
    if status is None:
        return False
    return status.timestamp >= recent_threshold(settings.device_online_seconds)


async def device_last_seen(device: Device) -> datetime | None:
    status = await latest_status(device)
    return status.timestamp if status else None
