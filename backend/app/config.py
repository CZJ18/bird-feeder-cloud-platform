from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _list_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = _int_env("DB_PORT", 3306)
    db_user: str = os.getenv("DB_USER", "birdcam_user")
    db_password: str = os.getenv("DB_PASSWORD", "change_me")
    db_name: str = os.getenv("DB_NAME", "birdcam_db")

    mqtt_host: str = os.getenv("MQTT_HOST", "127.0.0.1")
    mqtt_port: int = _int_env("MQTT_PORT", 8883)
    mqtt_user: str = os.getenv("MQTT_USER", "mqtt_user")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "mqtt_pass")
    mqtt_tls_ca_path: str = os.getenv("MQTT_TLS_CA_PATH", "./certs/ca.crt")
    mqtt_topic_event: str = os.getenv("MQTT_TOPIC_EVENT", "birdcam/event")
    mqtt_topic_status: str = os.getenv("MQTT_TOPIC_STATUS", "birdcam/status")
    mqtt_reconnect_interval_seconds: int = _int_env("MQTT_RECONNECT_INTERVAL_SECONDS", 5)

    upload_base_dir: str = os.getenv("UPLOAD_BASE_DIR", "./app/static/uploads/low_confidence")
    upload_public_prefix: str = os.getenv("UPLOAD_PUBLIC_PREFIX", "/uploads/low_confidence")
    max_upload_size_mb: int = _int_env("MAX_UPLOAD_SIZE_MB", 10)

    dashboard_api_token: str = os.getenv("DASHBOARD_API_TOKEN", "change_me_to_a_long_random_token")
    device_api_key_length: int = _int_env("DEVICE_API_KEY_LENGTH", 64)
    device_online_seconds: int = _int_env("DEVICE_ONLINE_SECONDS", 300)

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = _int_env("API_PORT", 8000)
    debug: bool = _bool_env("DEBUG", False)
    enable_mqtt: bool = _bool_env("ENABLE_MQTT", False)
    auto_create_device_from_mqtt: bool = _bool_env("AUTO_CREATE_DEVICE_FROM_MQTT", True)
    cors_origins: list[str] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "cors_origins",
            _list_env("CORS_ORIGINS", ["http://localhost:3000", "http://127.0.0.1:3000"]),
        )

    @property
    def mysql_url(self) -> str:
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def upload_root(self) -> Path:
        return Path(self.upload_base_dir).resolve()

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}


def is_allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""
