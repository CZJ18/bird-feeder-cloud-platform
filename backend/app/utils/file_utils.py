from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import file_extension, is_allowed_image, settings


async def save_upload_image(image: UploadFile, device_id: str, timestamp: float) -> tuple[str, str]:
    """Validate and save a low-confidence image upload."""
    if not image.filename or not is_allowed_image(image.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported image type")

    content = await image.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="image too large")

    ext = file_extension(image.filename) or "jpg"
    day = str(int(timestamp))[:10]
    from datetime import datetime

    day_dir_name = datetime.fromtimestamp(float(timestamp)).strftime("%Y%m%d")
    target_dir = settings.upload_root / day_dir_name
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{device_id}_{day}_{uuid.uuid4().hex[:12]}.{ext}"
    file_path = target_dir / filename
    file_path.write_bytes(content)

    public_url = f"{settings.upload_public_prefix}/{day_dir_name}/{filename}"
    return str(file_path), public_url
