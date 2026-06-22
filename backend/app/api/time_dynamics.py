from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import api_success
from app.services.statistics import time_dynamics

router = APIRouter()


@router.get("/time-dynamics")
async def get_time_dynamics(days: int = 7, unit: str = "day") -> dict[str, object]:
    return api_success({"regionData": await time_dynamics(days, unit)})
