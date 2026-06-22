from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import close_database, init_database
from scripts.seed_devices import seed_devices
from scripts.seed_species import seed_species


async def main() -> None:
    await init_database(generate_schemas=True)
    await seed_species()
    created_keys = await seed_devices()
    Path("logs").mkdir(exist_ok=True)
    key_file = Path("logs/init_devices_keys.txt")
    if created_keys:
        key_file.write_text("\n".join(f"{device_id},{api_key}" for device_id, api_key in created_keys), encoding="utf-8")
        print(f"Created {len(created_keys)} device API keys. See {key_file}")
    else:
        print("Species and 12 devices already initialized.")
    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
