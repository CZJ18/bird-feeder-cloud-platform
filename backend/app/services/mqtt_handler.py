from __future__ import annotations

from decimal import Decimal
from typing import Any

from loguru import logger

from app.config import settings
from app.models import Device, DeviceStatus, EventLeave, SpeciesDict, SystemLog
from app.services.device_service import get_or_create_device
from app.utils.time_utils import from_unix_seconds


async def handle_event_message(payload: dict[str, Any]) -> EventLeave | None:
    """Persist leave events and ignore enter events."""
    event_type = payload.get("event_type")
    if event_type == "enter":
        logger.bind(channel="mqtt").info("ignored enter event: {}", payload.get("device_id"))
        return None
    if event_type != "leave":
        logger.bind(channel="mqtt").warning("ignored unknown event type: {}", event_type)
        return None

    device_id = str(payload["device_id"])
    if settings.auto_create_device_from_mqtt:
        device = await get_or_create_device(device_id)
    else:
        device = await Device.get_or_none(device_id=device_id)
        if not device:
            raise ValueError(f"unknown device_id: {device_id}")

    species = await SpeciesDict.get_or_none(class_id=payload.get("class_id"))
    event = await EventLeave.create(
        track_id=int(payload.get("track_id", 0)),
        device=device,
        timestamp=from_unix_seconds(payload.get("timestamp")),
        confidence=Decimal(str(payload.get("confidence", 0))),
        box_x1=Decimal(str(payload.get("x1", 0))),
        box_y1=Decimal(str(payload.get("y1", 0))),
        box_x2=Decimal(str(payload.get("x2", 0))),
        box_y2=Decimal(str(payload.get("y2", 0))),
        species=species,
        species_name=species.species_cn if species else None,
        video_path=payload.get("video_path"),
        raw_payload=payload,
    )
    await SystemLog.create(
        device=device,
        type="INFO",
        source="mqtt",
        message=f"识别到 leave 事件: {event.species_name or payload.get('class_id')}",
    )
    return event


async def handle_status_message(payload: dict[str, Any]) -> DeviceStatus:
    """Persist device status messages."""
    device = await get_or_create_device(str(payload["device_id"]))
    memory = payload.get("memory_usage") or {}
    disk = payload.get("disk_usage") or {}
    status = await DeviceStatus.create(
        device=device,
        timestamp=from_unix_seconds(payload.get("timestamp")),
        cpu_temperature=payload.get("cpu_temperature"),
        mem_total_mb=memory.get("total_mb"),
        mem_available_mb=memory.get("available_mb"),
        mem_percent=memory.get("percent"),
        disk_total_gb=disk.get("total_gb"),
        disk_free_gb=disk.get("free_gb"),
        disk_percent=disk.get("percent"),
        battery=payload.get("battery"),
        food_level=payload.get("food_level"),
        network=payload.get("network"),
        raw_payload=payload,
    )
    await SystemLog.create(device=device, type="INFO", source="mqtt", message="设备状态上报")
    return status
