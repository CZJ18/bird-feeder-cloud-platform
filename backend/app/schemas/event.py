from __future__ import annotations

from pydantic import BaseModel


class HistorySummary(BaseModel):
    total_count: int
    species_count: int
    today_count: int
    avg_confidence: float
