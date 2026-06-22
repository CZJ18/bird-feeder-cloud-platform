from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from fastapi import HTTPException
from starlette.responses import StreamingResponse

from app.config import settings
from app.models import Moment


@dataclass(frozen=True)
class EdgeRecording:
    path: str
    name: str
    date: str
    species: str
    duration: float | None
    confidence: float | None
    size_mb: float | None


def _edge_base_url() -> str:
    if not settings.edge_recordings_base_url:
        raise HTTPException(status_code=500, detail="EDGE_RECORDINGS_BASE_URL is not configured")
    return settings.edge_recordings_base_url.rstrip("/")


def _edge_headers(accept: str = "application/json", range_header: str | None = None) -> dict[str, str]:
    headers = {"Accept": accept}
    if settings.edge_recordings_api_token:
        headers["X-API-Token"] = settings.edge_recordings_api_token
    if range_header:
        headers["Range"] = range_header
    return headers


def _read_url(url: str, accept: str = "application/json") -> bytes:
    request = Request(url, headers=_edge_headers(accept=accept))
    with urlopen(request, timeout=10) as response:
        return response.read()


def _list_recordings_sync() -> list[dict[str, object]]:
    payload = _read_url(f"{_edge_base_url()}/api/recordings")
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, list):
        raise HTTPException(status_code=502, detail="Unexpected edge recordings response")
    return data


async def list_edge_recordings() -> list[EdgeRecording]:
    rows = await asyncio.to_thread(_list_recordings_sync)
    recordings: list[EdgeRecording] = []
    for row in rows:
        path = str(row.get("path") or "")
        if not path.lower().endswith(".mp4"):
            continue
        recordings.append(
            EdgeRecording(
                path=path,
                name=str(row.get("name") or path.rsplit("/", 1)[-1]),
                date=str(row.get("date") or ""),
                species=str(row.get("species") or row.get("species_en") or "unknown"),
                duration=float(row["event_duration"]) if row.get("event_duration") is not None else None,
                confidence=float(row["confidence"]) if row.get("confidence") is not None else None,
                size_mb=float(row["size_mb"]) if row.get("size_mb") is not None else None,
            )
        )
    return recordings


def proxy_recording_url(path: str) -> str:
    return f"/api/recordings/{quote(path, safe='/')}"


async def sync_edge_recordings(limit: int | None = None) -> dict[str, int]:
    recordings = await list_edge_recordings()
    if limit:
        recordings = recordings[:limit]

    created = 0
    updated = 0
    for index, recording in enumerate(recordings):
        video_url = proxy_recording_url(recording.path)
        title = f"{recording.name} {recording.date}".strip()
        description = [
            f"path={recording.path}",
            f"duration={recording.duration or 0}",
            f"confidence={recording.confidence or 0}",
            f"size_mb={recording.size_mb or 0}",
        ]
        row = await Moment.filter(video_url=video_url).first()
        if row:
            row.title = title or recording.name
            row.sort_order = index
            row.is_active = True
            await row.save()
            updated += 1
        else:
            await Moment.create(
                title=title or recording.name,
                video_url=video_url,
                cover_image="",
                sort_order=index,
                is_active=True,
            )
            created += 1

    return {"total": len(recordings), "created": created, "updated": updated}


def _open_edge_video(path: str, range_header: str | None = None):
    url = urljoin(f"{_edge_base_url()}/api/recordings/", quote(path, safe="/"))
    request = Request(url, headers=_edge_headers(accept="video/mp4,*/*", range_header=range_header))
    return urlopen(request, timeout=10)


async def stream_edge_recording(path: str, range_header: str | None = None) -> StreamingResponse:
    try:
        response = await asyncio.to_thread(_open_edge_video, path, range_header)
    except HTTPError as exc:
        raise HTTPException(status_code=exc.code, detail=f"Edge recording is unavailable: {exc.reason}") from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"Edge recording source is unavailable: {exc.reason}") from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=502, detail="Edge recording source timed out") from exc

    def iterator():
        with response:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk

    headers = {"Accept-Ranges": "bytes"}
    for name in ("Content-Length", "Content-Range"):
        value = response.headers.get(name)
        if value:
            headers[name] = value

    return StreamingResponse(
        iterator(),
        status_code=getattr(response, "status", 200),
        media_type=response.headers.get("Content-Type", "video/mp4"),
        headers=headers,
    )
