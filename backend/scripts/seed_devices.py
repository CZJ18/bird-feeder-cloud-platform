from __future__ import annotations

import secrets
from datetime import date
from decimal import Decimal

from app.models import Device, DeviceConfig

DEVICES = [
    ("birdcam_001", "大围山观测点1", Decimal("28.4350000"), Decimal("114.1030000"), "大围山北坡"),
    ("birdcam_002", "大围山观测点2", Decimal("28.4365000"), Decimal("114.1052000"), "大围山溪谷"),
    ("birdcam_003", "湿地观测点1", Decimal("28.2280000"), Decimal("113.0810000"), "湿地保护区东侧"),
    ("birdcam_004", "湿地观测点2", Decimal("28.2293000"), Decimal("113.0835000"), "湿地保护区西侧"),
    ("birdcam_005", "校园林地1", Decimal("28.1801000"), Decimal("113.0322000"), "校园后山林地"),
    ("birdcam_006", "校园林地2", Decimal("28.1815000"), Decimal("113.0330000"), "校园花园"),
    ("birdcam_007", "果园观测点1", Decimal("28.3120000"), Decimal("113.4560000"), "郊区果园"),
    ("birdcam_008", "果园观测点2", Decimal("28.3135000"), Decimal("113.4580000"), "果园水渠旁"),
    ("birdcam_009", "森林公园1", Decimal("28.5010000"), Decimal("113.7710000"), "森林公园入口"),
    ("birdcam_010", "森林公园2", Decimal("28.5025000"), Decimal("113.7728000"), "森林公园深林区"),
    ("birdcam_011", "河岸观测点1", Decimal("28.2600000"), Decimal("113.1100000"), "河岸芦苇带"),
    ("birdcam_012", "河岸观测点2", Decimal("28.2617000"), Decimal("113.1123000"), "河岸浅滩"),
]


async def seed_devices() -> list[tuple[str, str]]:
    created_keys: list[tuple[str, str]] = []
    for device_id, name, latitude, longitude, location_desc in DEVICES:
        device = await Device.get_or_none(device_id=device_id)
        if device:
            await device.update_from_dict({
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "location_desc": location_desc,
                "status": 1,
            }).save()
        else:
            api_key = secrets.token_hex(32)
            device = await Device.create(
                device_id=device_id,
                name=name,
                api_key=api_key,
                latitude=latitude,
                longitude=longitude,
                location_desc=location_desc,
                install_date=date.today(),
                status=1,
            )
            created_keys.append((device.device_id, api_key))
        await DeviceConfig.get_or_create(device=device)
    return created_keys
