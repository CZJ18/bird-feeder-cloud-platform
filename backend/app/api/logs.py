from __future__ import annotations

from fastapi import APIRouter

from app.models import SystemLog
from app.schemas.common import ok_success

router = APIRouter()


@router.get("/device/logs")
async def get_device_logs(device_id: str | None = None, type: str | None = None) -> dict[str, object]:
    query = SystemLog.all().prefetch_related("device").order_by("-created_at")
    if device_id:
        query = query.filter(device__device_id=device_id)
    if type:
        query = query.filter(type=type)
    logs = []
    for row in await query:
        logs.append({
            "id": row.id,
            "device_id": row.device.device_id if row.device else "",
            "type": row.type,
            "message": row.message,
            "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return ok_success({"logs": logs})
