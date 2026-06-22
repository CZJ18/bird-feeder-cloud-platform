from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.models import LowConfidenceImage
from app.schemas.common import api_success
from app.schemas.low_confidence import LowConfidenceReviewIn
from app.utils.time_utils import parse_date

router = APIRouter()


@router.get("/low-confidence")
async def list_low_confidence(
    page: int = 1,
    size: int = 10,
    status: str = "pending",
    device_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, object]:
    query = LowConfidenceImage.all().prefetch_related("device", "species").order_by("-timestamp")
    if status != "all":
        query = query.filter(review_status=status)
    if device_id:
        query = query.filter(device__device_id=device_id)
    start = parse_date(start_date)
    end = parse_date(end_date)
    if start:
        query = query.filter(timestamp__gte=datetime.combine(start, datetime.min.time()))
    if end:
        query = query.filter(timestamp__lte=datetime.combine(end, datetime.max.time()))
    total = await query.count()
    rows = await query.offset((page - 1) * size).limit(size)
    return api_success({
        "total": total,
        "list": [
            {
                "id": row.id,
                "device": row.device.name or row.device.device_id,
                "device_id": row.device.device_id,
                "species": row.species_name or "未知",
                "confidence": float(row.confidence),
                "timestamp": row.timestamp.isoformat(timespec="seconds"),
                "image_url": row.image_url,
                "review_status": row.review_status,
            }
            for row in rows
        ],
    })


@router.put("/low-confidence/{image_id}")
async def review_low_confidence(image_id: int, payload: LowConfidenceReviewIn) -> dict[str, object]:
    row = await LowConfidenceImage.get_or_none(id=image_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="low confidence image not found")
    row.review_status = payload.review_status
    row.review_comment = payload.review_comment
    row.reviewed_at = datetime.now()
    await row.save()
    return api_success({"id": row.id, "review_status": row.review_status, "review_comment": row.review_comment})
