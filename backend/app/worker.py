from __future__ import annotations

import asyncio

from loguru import logger

from app.database import close_database, init_database
from app.mqtt_client.consumer import mqtt_consumer
from app.utils.logger import setup_logging


async def main() -> None:
    setup_logging()
    await init_database()
    logger.info("MQTT worker started")
    try:
        await mqtt_consumer()
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
