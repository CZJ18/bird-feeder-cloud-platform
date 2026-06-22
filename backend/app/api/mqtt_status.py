from __future__ import annotations

import asyncio
import ssl
import time
from datetime import datetime
from typing import Any

import aiomqtt
from fastapi import APIRouter
from loguru import logger

from app.config import settings
from app.models import DeviceStatus, EventLeave
from app.schemas.common import api_success
from app.utils.time_utils import iso

router = APIRouter()

SYS_TOPICS = {
    "$SYS/broker/version",
    "$SYS/broker/uptime",
    "$SYS/broker/clients/connected",
    "$SYS/broker/clients/active",
    "$SYS/broker/clients/total",
    "$SYS/broker/messages/received",
    "$SYS/broker/messages/sent",
    "$SYS/broker/publish/messages/received",
    "$SYS/broker/publish/messages/sent",
}

_CACHE: dict[str, Any] = {"expires_at": 0.0, "data": None}


def _number(value: str | None) -> int | float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def _tls_context() -> ssl.SSLContext | None:
    if not settings.mqtt_tls_ca_path:
        return None
    return ssl.create_default_context(cafile=settings.mqtt_tls_ca_path)


async def _collect_sys_status(wait_seconds: float = 2.5) -> dict[str, str]:
    values: dict[str, str] = {}
    async with aiomqtt.Client(
        hostname=settings.mqtt_host,
        port=settings.mqtt_port,
        username=settings.mqtt_user,
        password=settings.mqtt_password,
        tls_context=_tls_context(),
        identifier=f"birdcam-api-mqtt-status-{int(time.time() * 1000)}",
    ) as client:
        await client.subscribe("$SYS/broker/#")
        iterator = client.messages.__aiter__()
        deadline = time.monotonic() + wait_seconds
        while time.monotonic() < deadline and len(values) < len(SYS_TOPICS):
            try:
                message = await asyncio.wait_for(iterator.__anext__(), timeout=max(0.1, deadline - time.monotonic()))
            except asyncio.TimeoutError:
                break
            topic = str(message.topic)
            if topic in SYS_TOPICS:
                values[topic] = message.payload.decode("utf-8", "replace")
    return values


async def _business_status() -> dict[str, object]:
    event_count = await EventLeave.all().count()
    status_count = await DeviceStatus.all().count()
    latest_event = await EventLeave.all().order_by("-timestamp").first()
    latest_status = await DeviceStatus.all().order_by("-timestamp").first()

    latest_times: list[datetime] = []
    if latest_event:
        latest_times.append(latest_event.timestamp)
    if latest_status:
        latest_times.append(latest_status.timestamp)

    return {
        "event_count": event_count,
        "status_count": status_count,
        "latest_event_at": iso(latest_event.timestamp) if latest_event else None,
        "latest_status_at": iso(latest_status.timestamp) if latest_status else None,
        "latest_business_at": iso(max(latest_times)) if latest_times else None,
    }


@router.get("/mqtt/status")
async def get_mqtt_status() -> dict[str, object]:
    now = time.monotonic()
    if _CACHE["data"] is not None and now < float(_CACHE["expires_at"]):
        broker_status = _CACHE["data"]
    else:
        connected = False
        error: str | None = None
        sys_values: dict[str, str] = {}
        try:
            sys_values = await _collect_sys_status()
            connected = True
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            logger.bind(channel="mqtt").warning("mqtt status probe failed: {}", error)

        broker_status = {
            "connected": connected,
            "host": settings.mqtt_host,
            "port": settings.mqtt_port,
            "version": sys_values.get("$SYS/broker/version"),
            "uptime": sys_values.get("$SYS/broker/uptime"),
            "clients": {
                "connected": _number(sys_values.get("$SYS/broker/clients/connected")),
                "active": _number(sys_values.get("$SYS/broker/clients/active")),
                "total": _number(sys_values.get("$SYS/broker/clients/total")),
            },
            "messages": {
                "received": _number(sys_values.get("$SYS/broker/messages/received")),
                "sent": _number(sys_values.get("$SYS/broker/messages/sent")),
                "publish_received": _number(sys_values.get("$SYS/broker/publish/messages/received")),
                "publish_sent": _number(sys_values.get("$SYS/broker/publish/messages/sent")),
            },
            "error": error,
            "probed_at": datetime.now().isoformat(timespec="seconds"),
        }
        _CACHE.update({"data": broker_status, "expires_at": now + 10})

    return api_success({
        "broker": broker_status,
        "business": await _business_status(),
        "topics": {
            "event": settings.mqtt_topic_event,
            "status": settings.mqtt_topic_status,
        },
    })
