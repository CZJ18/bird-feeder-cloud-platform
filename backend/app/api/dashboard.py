from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import api_success
from app.services.statistics import dashboard_statistics, management_statistics

router = APIRouter()


@router.get("/dashboard/statistics")
async def get_dashboard_statistics() -> dict[str, object]:
    return api_success(await dashboard_statistics())


@router.get("/statistics")
async def get_management_statistics() -> dict[str, object]:
    return api_success(await management_statistics())
