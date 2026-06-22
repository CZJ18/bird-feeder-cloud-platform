from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api import dashboard, devices, events, logs, low_confidence, moments, monthly_trend, mqtt_status, species, time_dynamics
from app.dependencies import require_api_token

api_router = APIRouter(prefix="/api", dependencies=[Depends(require_api_token)])
api_router.include_router(dashboard.router)
api_router.include_router(species.router)
api_router.include_router(time_dynamics.router)
api_router.include_router(monthly_trend.router)
api_router.include_router(mqtt_status.router)
api_router.include_router(devices.router)
api_router.include_router(moments.router)
api_router.include_router(low_confidence.router)
api_router.include_router(events.router)
api_router.include_router(logs.router)
