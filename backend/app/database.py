from __future__ import annotations

from tortoise import Tortoise

from app.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.mysql_url},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}


async def init_database(generate_schemas: bool = False) -> None:
    """Initialize Tortoise ORM for the FastAPI process or scripts."""
    await Tortoise.init(config=TORTOISE_ORM)
    if generate_schemas:
        await Tortoise.generate_schemas()


async def close_database() -> None:
    """Close all Tortoise ORM connections."""
    await Tortoise.close_connections()
