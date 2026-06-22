from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, HTTPException, status
from tortoise.timezone import now

from app.models import Device, DeviceCommand, DeviceConfig, DeviceStatus
from app.schemas.common import api_success, ok_success
from app.schemas.device import DeviceCommandIn, DeviceConfigIn
from app.services.device_service import is_online
from app.services.statistics import devices_map
from app.utils.time_utils import iso

router = APIRouter()


async def _device_payload(device: Device) -> dict[str, object]:
    latest = await DeviceStatus.filter(device=device).order_by("-timestamp").first()
    return {
        "device_id": device.device_id,
        "name": device.name or device.device_id,
        "cpu_temperature": float(latest.cpu_temperature) if latest and latest.cpu_temperature is not None else None,
        "memory_usage": {
            "total_mb": float(latest.mem_total_mb) if latest and latest.mem_total_mb is not None else None,
            "available_mb": float(latest.mem_available_mb) if latest and latest.mem_available_mb is not None else None,
            "percent": float(latest.mem_percent) if latest and latest.mem_percent is not None else None,
        },
        "disk_usage": {
            "total_gb": float(latest.disk_total_gb) if latest and latest.disk_total_gb is not None else None,
            "free_gb": float(latest.disk_free_gb) if latest and latest.disk_free_gb is not None else None,
            "percent": float(latest.disk_percent) if latest and latest.disk_percent is not None else None,
        },
        "online": is_online(latest),
        "last_seen": iso(latest.timestamp) if latest else None,
    }


@router.get("/devices/status")
async def get_devices_status() -> dict[str, object]:
    devices = await Device.all()
    return api_success({"devices": [await _device_payload(device) for device in devices]})


@router.get("/devices/map")
async def get_devices_map(start_year: int | None = None, end_year: int | None = None) -> dict[str, object]:
    current = date.today().year
    return api_success(await devices_map(start_year or current - 4, end_year or current))


@router.get("/device/list")
async def get_device_list() -> dict[str, object]:
    rows = []
    for device in await Device.all():
        latest = await DeviceStatus.filter(device=device).order_by("-timestamp").first()
        rows.append({
            "device_id": device.device_id,
            "name": device.name or device.device_id,
            "location": device.location_desc or "",
            "status": "online" if is_online(latest) else "offline",
            "battery": latest.battery if latest and latest.battery is not None else 0,
            "food_level": latest.food_level if latest and latest.food_level is not None else 0,
            "network": latest.network if latest and latest.network else "4G",
            "last_online": latest.timestamp.strftime("%Y-%m-%d %H:%M:%S") if latest else "",
        })
    return ok_success({"devices": rows})


@router.get("/device/config/{device_id}")
async def get_device_config(device_id: str) -> dict[str, object]:
    device = await Device.get_or_none(device_id=device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found")
    config = await DeviceConfig.get_or_none(device=device)
    if not config:
        config = await DeviceConfig.create(device=device)
    return ok_success({
        "device_id": device.device_id,
        "capture_interval": config.capture_interval,
        "confidence_threshold": float(config.confidence_threshold),
        "upload_image": config.upload_image,
        "night_mode": config.night_mode,
        "low_battery_threshold": config.low_battery_threshold,
    })


@router.post("/device/config/{device_id}")
async def update_device_config(device_id: str, payload: DeviceConfigIn) -> dict[str, object]:
    device = await Device.get_or_none(device_id=device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found")
    config = await DeviceConfig.get_or_none(device=device)
    values = payload.model_dump()
    if config:
        await config.update_from_dict(values).save()
    else:
        config = await DeviceConfig.create(device=device, **values)
    return ok_success({
        "device_id": device.device_id,
        "capture_interval": config.capture_interval,
        "confidence_threshold": float(config.confidence_threshold),
        "upload_image": config.upload_image,
        "night_mode": config.night_mode,
        "low_battery_threshold": config.low_battery_threshold,
    }, "配置更新成功")


@router.post("/device/command")
async def send_device_command(payload: DeviceCommandIn) -> dict[str, object]:
    command_map = {"capture": "take_photo", "take_photo": "take_photo", "restart": "restart", "update": "update_config", "update_config": "update_config"}
    if payload.command not in command_map:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid command")
    device = await Device.get_or_none(device_id=payload.device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found")
    command = await DeviceCommand.create(device=device, command=command_map[payload.command], status="pending")
    return ok_success({
        "id": command.id,
        "device_id": device.device_id,
        "command": command.command,
        "status": command.status,
        "created_at": command.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }, "命令已下发")
