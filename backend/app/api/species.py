from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import api_success
from app.services.statistics import species_distribution

router = APIRouter()


@router.get("/species/distribution")
async def get_species_distribution(top: int = 10, start_date: str | None = None, end_date: str | None = None) -> dict[str, object]:
    return api_success({"regionData": await species_distribution(top, start_date, end_date)})
