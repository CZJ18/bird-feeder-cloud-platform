from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from app.schemas.common import api_success
from app.services.statistics import monthly_trend

router = APIRouter()


@router.get("/monthly-trend")
async def get_monthly_trend(year: int | None = None, top: int = 8) -> dict[str, object]:
    return api_success(await monthly_trend(year or date.today().year, top))
