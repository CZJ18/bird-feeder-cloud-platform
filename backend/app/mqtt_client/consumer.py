from __future__ import annotations

import asyncio
import json
import ssl

import aiomqtt
from loguru import logger

from app.config import settings
from app.services.mqtt_handler import handle_event_message, handle_status_message


def _tls_context() -> ssl.SSLContext | None:
    if not settings.mqtt_tls_ca_path:
        return None
    context = ssl.create_default_context(cafile=settings.mqtt_tls_ca_path)
    return context


async def mqtt_consumer() -> None:
    """Connect to MQTT broker, subscribe to event/status topics, and reconnect forever."""
    topics = [settings.mqtt_topic_event, settings.mqtt_topic_status]
    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.mqtt_host,
                port=settings.mqtt_port,
                username=settings.mqtt_user,
                password=settings.mqtt_password,
                tls_context=_tls_context(),
            ) as client:
                for topic in topics:
                    await client.subscribe(topic)
                    logger.bind(channel="mqtt").info("subscribed mqtt topic: {}", topic)
                async for message in client.messages:
                    try:
                        payload = json.loads(message.payload.decode("utf-8"))
                        topic = str(message.topic)
                        logger.bind(channel="mqtt").info("received mqtt message: {}", topic)
                        if topic == settings.mqtt_topic_event:
                            await handle_event_message(payload)
                        elif topic == settings.mqtt_topic_status:
                            await handle_status_message(payload)
                    except Exception as exc:
                        logger.bind(channel="mqtt").exception("mqtt message handling failed: {}", exc)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.bind(channel="mqtt").exception("mqtt connection failed: {}", exc)
            await asyncio.sleep(settings.mqtt_reconnect_interval_seconds)
