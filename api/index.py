import os
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DEFAULT_TOKEN = "e7a9341f78ad2c6c1107a3566fac30eb"

if os.getenv("VERCEL"):
    os.environ.setdefault("ENABLE_MQTT", "false")
    os.environ.setdefault("DASHBOARD_API_TOKEN", DEFAULT_TOKEN)
    os.environ.setdefault("UPLOAD_BASE_DIR", "/tmp/uploads/low_confidence")
    os.environ.setdefault("UPLOAD_PUBLIC_PREFIX", "/uploads/low_confidence")

has_database_env = bool(os.getenv("DB_HOST") and os.getenv("DB_PASSWORD") and os.getenv("DB_NAME"))
app = FastAPI(title="鸟类智能监测系统后端 Mock", version="1.0.0")


def require_token(x_api_token: str | None) -> None:
    if x_api_token not in {os.getenv("DASHBOARD_API_TOKEN"), DEFAULT_TOKEN, "change_me_to_a_long_random_token"}:
        raise HTTPException(status_code=401, detail="invalid api token")


def ok(data):
    return {"code": 200, "message": "success", "data": data}


if os.getenv("VERCEL") and not has_database_env:
    species = [
        {"name": "白鹭", "value": 56},
        {"name": "麻雀", "value": 51},
        {"name": "喜鹊", "value": 40},
        {"name": "乌鸦", "value": 25},
        {"name": "斑鸠", "value": 25},
        {"name": "燕子", "value": 25},
        {"name": "杜鹃", "value": 25},
    ]

    @app.get("/")
    async def root():
        return ok({"name": "鸟类智能监测系统后端 Mock", "version": "1.0.0"})

    @app.get("/api/dashboard/statistics")
    async def dashboard_statistics(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({
            "speciesStats": {"totalVisits": 23456, "totalSpecies": 28, "onlineCount": 3},
            "kpiCard": {"todayNew": 128, "todayActive": 3, "pendingReview": 6, "avgConfidence": 92, "todaySpeciesCount": 5},
        })

    @app.get("/api/statistics")
    async def statistics(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({
            "daily_counts": [{"date": f"2026-06-{day:02d}", "count": 50 + day * 3} for day in range(1, 15)],
            "species_counts": [{"name": item["name"], "count": item["value"]} for item in species],
            "device_upload_counts": [
                {"device_id": "BIRD-001", "device_name": "摄像头监测点1", "upload_count": 380},
                {"device_id": "BIRD-002", "device_name": "鸟类识别终端1", "upload_count": 250},
            ],
            "food_level_trend": [{"date": "2026-06-16", "food_level": 72}],
        })

    @app.get("/api/species/distribution")
    async def species_distribution(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"regionData": species})

    @app.get("/api/time-dynamics")
    async def time_dynamics(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        values = [72, 96, 81, 118, 132, 104, 145]
        return ok({"regionData": [{"id": index + 1, "mdate": day, "value": value, "temperature": 28 + index % 3} for index, (day, value) in enumerate(zip(days, values))]})

    @app.get("/api/monthly-trend")
    async def monthly_trend(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({
            "dimensions": [f"{month}月" for month in range(1, 13)],
            "data": [
                {"species": "白鹭", "values": [32, 38, 46, 62, 81, 88, 76, 72, 68, 54, 42, 36]},
                {"species": "麻雀", "values": [72, 69, 74, 78, 82, 86, 88, 84, 79, 76, 73, 70]},
            ],
        })

    @app.get("/api/devices/status")
    async def devices_status(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"devices": [
            {"device_id": "BIRD-001", "name": "摄像头监测点1", "cpu_temperature": 46.5, "memory_usage": {"total_mb": 4096, "available_mb": 1880, "percent": 54.1}, "disk_usage": {"total_gb": 64, "free_gb": 41.2, "percent": 35.6}, "online": True, "last_seen": datetime.now().isoformat(timespec="seconds")}
        ]})

    @app.get("/api/devices/map")
    async def devices_map(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"voltageLevel": ["2021", "2022", "2023", "2024", "2025"], "categoryData": {}, "topData": {}, "colors": ["#35e8ff", "#57ffad"]})

    @app.get("/api/device/list")
    async def device_list(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"devices": [{"device_id": "BIRD-001", "name": "摄像头监测点1", "location": "湖南农业大学", "status": "online", "battery": 86, "food_level": 72, "network": "WiFi", "last_online": datetime.now().isoformat(timespec="seconds")}]})

    @app.post("/api/device/command")
    async def device_command(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"status": "pending"})

    @app.get("/api/moments")
    async def moments(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"regionData": [{"id": 1, "videoUrl": "", "title": "白鹭群居瞬间回放", "coverImage": None}]})

    @app.get("/api/low-confidence")
    async def low_confidence(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"total": 0, "list": []})

    @app.get("/api/bird/events")
    async def bird_events(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"events": []})

    @app.get("/api/bird/history")
    async def bird_history(x_api_token: str | None = Header(default=None, alias="X-API-Token")):
        require_token(x_api_token)
        return ok({"total": 0, "records": [], "summary": {"avg_confidence": 0.92}})

else:
    if str(BACKEND) not in sys.path:
        sys.path.insert(0, str(BACKEND))
    from app.main import app as real_app

    app = real_app
