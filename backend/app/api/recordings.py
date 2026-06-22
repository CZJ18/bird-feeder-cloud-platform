from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas.common import api_success
from app.services.edge_recordings import stream_edge_recording, sync_edge_recordings

router = APIRouter()
public_router = APIRouter(prefix="/api")


@router.post("/recordings/sync")
async def sync_recordings(limit: int | None = None) -> dict[str, object]:
    return api_success(await sync_edge_recordings(limit))


@public_router.get("/recordings/{recording_path:path}")
async def get_recording(recording_path: str, request: Request):
    return await stream_edge_recording(recording_path, request.headers.get("range"))
