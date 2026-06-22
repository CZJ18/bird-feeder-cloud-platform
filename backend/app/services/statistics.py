from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from app.config import settings
from app.models import Device, DeviceStatus, EventLeave, LowConfidenceImage, Moment
from app.services.device_service import is_online
from app.utils.time_utils import day_bounds, parse_date


async def dashboard_statistics() -> dict[str, object]:
    today_start, today_end = day_bounds()
    total_visits = await EventLeave.all().count()
    all_events = await EventLeave.all()
    total_species = len({event.species_id for event in all_events if event.species_id is not None})
    pending_review = await LowConfidenceImage.filter(review_status="pending").count()
    today_events = await EventLeave.filter(timestamp__gte=today_start, timestamp__lte=today_end)
    all_devices = await Device.all()

    online_count = 0
    today_active_ids: set[int] = set()
    today_species_ids: set[int] = set()

    for device in all_devices:
        status = await DeviceStatus.filter(device=device).order_by("-timestamp").first()
        if is_online(status):
            online_count += 1
        if status and today_start <= status.timestamp <= today_end:
            today_active_ids.add(device.id)

    for event in today_events:
        today_active_ids.add(event.device_id)
        if event.species_id is not None:
            today_species_ids.add(event.species_id)

    avg_confidence = round(sum(float(event.confidence) for event in all_events) / len(all_events) * 100) if all_events else 0
    return {
        "speciesStats": {
            "totalVisits": total_visits,
            "totalSpecies": total_species,
            "onlineCount": online_count,
        },
        "kpiCard": {
            "todayNew": len(today_events),
            "todayActive": len(today_active_ids),
            "pendingReview": pending_review,
            "avgConfidence": avg_confidence,
            "todaySpeciesCount": len(today_species_ids),
        },
    }


async def species_distribution(top: int = 10, start_date: str | None = None, end_date: str | None = None) -> list[dict[str, object]]:
    query = EventLeave.all()
    start = parse_date(start_date)
    end = parse_date(end_date)
    if start:
        query = query.filter(timestamp__gte=datetime.combine(start, datetime.min.time()))
    if end:
        query = query.filter(timestamp__lte=datetime.combine(end, datetime.max.time()))
    counts: dict[str, int] = defaultdict(int)
    for event in await query:
        counts[event.species_name or "未知"] += 1
    return [{"name": name, "value": count} for name, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:top]]


async def time_dynamics(days: int = 7, unit: str = "day") -> list[dict[str, object]]:
    since = datetime.now() - timedelta(days=days)
    events = await EventLeave.filter(timestamp__gte=since)
    statuses = await DeviceStatus.filter(timestamp__gte=since)
    event_counts: dict[str, int] = defaultdict(int)
    temps: dict[str, list[float]] = defaultdict(list)

    def bucket(dt: datetime) -> str:
        if unit == "month":
            return dt.strftime("%Y-%m")
        if unit == "week":
            year, week, _ = dt.isocalendar()
            return f"{year}-W{week:02d}"
        return dt.strftime("%Y-%m-%d")

    for event in events:
        event_counts[bucket(event.timestamp)] += 1
    for status in statuses:
        if status.cpu_temperature is not None:
            temps[bucket(status.timestamp)].append(float(status.cpu_temperature))

    keys = sorted(set(event_counts) | set(temps))
    return [
        {
            "id": index + 1,
            "mdate": key,
            "value": event_counts.get(key, 0),
            "temperature": round(sum(temps[key]) / len(temps[key]), 2) if temps.get(key) else None,
        }
        for index, key in enumerate(keys)
    ]


async def monthly_trend(year: int, top: int = 8) -> dict[str, object]:
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    events = await EventLeave.filter(timestamp__gte=start, timestamp__lte=end)
    species_totals: dict[str, int] = defaultdict(int)
    month_counts: dict[str, list[int]] = defaultdict(lambda: [0] * 12)
    for event in events:
        name = event.species_name or "未知"
        species_totals[name] += 1
        month_counts[name][event.timestamp.month - 1] += 1
    selected = [name for name, _ in sorted(species_totals.items(), key=lambda item: item[1], reverse=True)[:top]]
    return {
        "dimensions": [f"{month}月" for month in range(1, 13)],
        "data": [{"species": name, "values": month_counts[name]} for name in selected],
    }


async def devices_map(start_year: int, end_year: int) -> dict[str, object]:
    devices = await Device.all()
    years = [str(year) for year in range(start_year, end_year + 1)]
    category_data: dict[str, list[dict[str, object]]] = {}
    top_data: dict[str, list[dict[str, object]]] = {}
    for year_text in years:
        year = int(year_text)
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
        category_data[year_text] = []
        top_data[year_text] = []
        for device in devices:
            count = await EventLeave.filter(device=device, timestamp__gte=start, timestamp__lte=end).count()
            name = device.name or device.device_id
            category_data[year_text].append({"name": name, "value": count})
            if device.longitude is not None and device.latitude is not None:
                top_data[year_text].append({"name": name, "value": [float(device.longitude), float(device.latitude), count]})
    return {
        "voltageLevel": years,
        "categoryData": category_data,
        "topData": top_data,
        "colors": ["#1de9b6", "#f46e36", "#04b9ff", "#5dbd32", "#ffc809"],
    }


async def moments(limit: int = 10) -> list[dict[str, object]]:
    rows = await Moment.filter(is_active=True).order_by("sort_order", "-created_at").limit(limit)
    return [{"id": item.id, "videoUrl": item.video_url, "title": item.title, "coverImage": item.cover_image} for item in rows]


async def management_statistics() -> dict[str, object]:
    today = date.today()
    daily_counts = []
    for offset in range(29, -1, -1):
        current = today - timedelta(days=offset)
        start, end = day_bounds(current)
        daily_counts.append({"date": current.isoformat(), "count": await EventLeave.filter(timestamp__gte=start, timestamp__lte=end).count()})
    species_counts = [{"name": row["name"], "count": row["value"]} for row in await species_distribution(top=20)]
    device_upload_counts = []
    food_level_trend = []
    for device in await Device.all():
        count = await EventLeave.filter(device=device).count()
        device_upload_counts.append({"device_id": device.device_id, "device_name": device.name or device.device_id, "upload_count": count})
        status = await DeviceStatus.filter(device=device).order_by("-timestamp").first()
        if status and status.food_level is not None:
            food_level_trend.append({"date": status.timestamp.date().isoformat(), "food_level": status.food_level})
    return {
        "daily_counts": daily_counts,
        "species_counts": species_counts,
        "device_upload_counts": sorted(device_upload_counts, key=lambda item: item["upload_count"], reverse=True),
        "food_level_trend": food_level_trend,
    }
