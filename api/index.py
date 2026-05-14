import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

os.environ.setdefault("UPLOAD_DIR", "/tmp/uploads" if os.getenv("VERCEL") else str(BACKEND / "uploads"))
os.environ.setdefault("SQLITE_DB_PATH", "/tmp/app.db" if os.getenv("VERCEL") else str(BACKEND / "app.db"))

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.main import app
