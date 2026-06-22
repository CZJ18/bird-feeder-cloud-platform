from __future__ import annotations

import os
from pathlib import Path

from loguru import logger


def setup_logging() -> None:
    log_dir = Path("/tmp/logs") if os.getenv("VERCEL") else Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(log_dir / "app.log", rotation="10 MB", retention=10, encoding="utf-8")
    logger.add(log_dir / "mqtt.log", rotation="10 MB", retention=10, encoding="utf-8", filter=lambda record: record["extra"].get("channel") == "mqtt")
    logger.add(log_dir / "upload.log", rotation="10 MB", retention=10, encoding="utf-8", filter=lambda record: record["extra"].get("channel") == "upload")
