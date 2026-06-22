from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.api.router import api_router
from app.api.recordings import public_router as public_recordings_router
from app.api.upload import router as upload_router
from app.config import settings
from app.database import close_database, init_database
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_database()
    settings.upload_root.parent.mkdir(parents=True, exist_ok=True)

    mqtt_task: asyncio.Task | None = None
    if settings.enable_mqtt:
        from app.mqtt_client.consumer import mqtt_consumer

        mqtt_task = asyncio.create_task(mqtt_consumer())
        logger.info("MQTT consumer started inside FastAPI process")

    try:
        yield
    finally:
        if mqtt_task:
            mqtt_task.cancel()
            try:
                await mqtt_task
            except asyncio.CancelledError:
                logger.info("MQTT consumer stopped")
        await close_database()


app = FastAPI(title="鸟类智能监测系统后端", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_root = settings.upload_root.parent
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(static_root)), name="uploads")
app.include_router(public_recordings_router)
app.include_router(api_router)
app.include_router(upload_router)


@app.get("/")
async def root() -> dict[str, object]:
    return {"code": 200, "message": "success", "data": {"name": "鸟类智能监测系统后端", "version": "1.0.0"}}


@app.get("/health")
async def health() -> dict[str, object]:
    return {"code": 200, "message": "ok"}
