from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import api_success
from app.services.statistics import moments

router = APIRouter()


@router.get("/moments")
async def get_moments(limit: int = 10) -> dict[str, object]:
    return api_success({"regionData": await moments(limit)})
