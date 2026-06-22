from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.services.upload_service import upload_low_confidence_image

router = APIRouter()


@router.post("/upload")
async def upload_image(
    image: UploadFile = File(...),
    x1: float = Form(...),
    y1: float = Form(...),
    x2: float = Form(...),
    y2: float = Form(...),
    confidence: float = Form(...),
    class_id: int = Form(...),
    timestamp: float = Form(...),
    rule_triggered: str | None = Form(default=None),
    device_id: str = Form(...),
    api_key: str = Form(...),
) -> dict[str, str]:
    row = await upload_low_confidence_image(
        image=image,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        confidence=confidence,
        class_id=class_id,
        timestamp=timestamp,
        rule_triggered=rule_triggered,
        device_id=device_id,
        api_key=api_key,
    )
    return {"status": "ok", "path": row.image_url}
