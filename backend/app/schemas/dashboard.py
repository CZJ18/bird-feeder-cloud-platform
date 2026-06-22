from __future__ import annotations

from pydantic import BaseModel


class SpeciesStats(BaseModel):
    totalVisits: int
    totalSpecies: int
    onlineCount: int


class KpiCard(BaseModel):
    todayNew: int
    todayActive: int
    pendingReview: int
    avgConfidence: int
    todaySpeciesCount: int


class DashboardStatistics(BaseModel):
    speciesStats: SpeciesStats
    kpiCard: KpiCard
