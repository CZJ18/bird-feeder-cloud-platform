from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Response

from app.models import DeviceStatus, EventLeave
from app.schemas.common import ok_success
from app.utils.time_utils import day_bounds

router = APIRouter()


async def _event_payload(event: EventLeave) -> dict[str, object]:
    latest = await DeviceStatus.filter(device=event.device).order_by("-timestamp").first()
    raw_payload = event.raw_payload or {}
    return {
        "id": event.id,
        "device_id": event.device.device_id,
        "bird_name": event.species_name or "未知",
        "class_id": raw_payload.get("class_id"),
        "track_id": event.track_id,
        "event_type": raw_payload.get("event_type"),
        "confidence": float(event.confidence),
        "image_url": "",
        "video_path": event.video_path or raw_payload.get("video_path") or "",
        "box": {
            "x1": float(event.box_x1),
            "y1": float(event.box_y1),
            "x2": float(event.box_x2),
            "y2": float(event.box_y2),
        },
        "temperature": raw_payload.get("temperature"),
        "humidity": raw_payload.get("humidity"),
        "battery": latest.battery if latest and latest.battery is not None else 0,
        "food_level": latest.food_level if latest and latest.food_level is not None else 0,
        "location": event.device.location_desc or "",
        "created_at": event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    }


@router.get("/bird/events")
async def get_bird_events(device_id: str | None = None, bird_name: str | None = None, limit: int | None = None) -> dict[str, object]:
    query = EventLeave.all().prefetch_related("device").order_by("-timestamp")
    if device_id:
        query = query.filter(device__device_id=device_id)
    if bird_name:
        query = query.filter(species_name__contains=bird_name)
    if limit:
        query = query.limit(limit)
    return ok_success({"events": [await _event_payload(event) for event in await query]})


@router.get("/bird/history")
async def get_bird_history(
    device_id: str | None = None,
    bird_name: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    min_confidence: float | None = None,
    max_confidence: float | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict[str, object]:
    query = EventLeave.all().prefetch_related("device").order_by("-timestamp")
    if device_id:
        query = query.filter(device__device_id=device_id)
    if bird_name:
        query = query.filter(species_name__contains=bird_name)
    if start_time:
        query = query.filter(timestamp__gte=datetime.fromisoformat(start_time.replace(" ", "T")))
    if end_time:
        query = query.filter(timestamp__lte=datetime.fromisoformat(end_time.replace(" ", "T")))
    if min_confidence is not None:
        query = query.filter(confidence__gte=min_confidence)
    if max_confidence is not None:
        query = query.filter(confidence__lte=max_confidence)
    total = await query.count()
    rows = await query.offset((page - 1) * page_size).limit(page_size)
    payloads = [await _event_payload(event) for event in rows]
    today_start, today_end = day_bounds()
    all_rows = await query
    species = {event.species_name for event in all_rows if event.species_name}
    avg = sum(float(event.confidence) for event in all_rows) / len(all_rows) if all_rows else 0
    return ok_success({
        "total": total,
        "records": payloads,
        "summary": {
            "total_count": total,
            "species_count": len(species),
            "today_count": len([event for event in all_rows if today_start <= event.timestamp <= today_end]),
            "avg_confidence": round(avg, 4),
        },
    })


@router.get("/bird/history/export")
async def export_bird_history() -> Response:
    rows = await EventLeave.all().prefetch_related("device").order_by("-timestamp")
    header = "ID,设备ID,鸟类名称,置信度,电池,饲料余量,位置,时间"
    lines = [header]
    for event in rows:
        payload = await _event_payload(event)
        lines.append(",".join(str(payload[key]) for key in ["id", "device_id", "bird_name", "confidence", "battery", "food_level", "location", "created_at"]))
    return Response(content="\ufeff" + "\n".join(lines), media_type="text/csv;charset=utf-8")
