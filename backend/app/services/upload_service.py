from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, UploadFile, status

from app.models import Device, LowConfidenceImage, SpeciesDict, SystemLog
from app.utils.file_utils import save_upload_image
from app.utils.time_utils import from_unix_seconds


async def upload_low_confidence_image(
    image: UploadFile,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    confidence: float,
    class_id: int,
    timestamp: float,
    rule_triggered: str | None,
    device_id: str,
    api_key: str,
) -> LowConfidenceImage:
    """Authenticate the device, save the uploaded image, and persist metadata."""
    device = await Device.get_or_none(device_id=device_id, api_key=api_key, status=1)
    if not device:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid device api key")
    species = await SpeciesDict.get_or_none(class_id=class_id)
    image_path, image_url = await save_upload_image(image, device_id, timestamp)
    row = await LowConfidenceImage.create(
        device=device,
        timestamp=from_unix_seconds(timestamp),
        confidence=Decimal(str(confidence)),
        species=species,
        species_name=species.species_cn if species else None,
        box_x1=Decimal(str(x1)),
        box_y1=Decimal(str(y1)),
        box_x2=Decimal(str(x2)),
        box_y2=Decimal(str(y2)),
        rule_triggered=rule_triggered,
        image_path=image_path,
        image_url=image_url,
        review_status="pending",
        raw_payload={
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "confidence": confidence,
            "class_id": class_id,
            "timestamp": timestamp,
            "rule_triggered": rule_triggered,
            "device_id": device_id,
        },
    )
    await SystemLog.create(device=device, type="INFO", source="upload", message="低置信度图片上传成功")
    return row
