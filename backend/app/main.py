from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import device, bird, statistics, logs
from app.database import init_db
from app.config import UPLOAD_DIR
import os

app = FastAPI(title="智能喂鸟器云端管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(device.router, prefix="/api", tags=["device"])
app.include_router(bird.router, prefix="/api", tags=["bird"])
app.include_router(statistics.router, prefix="/api", tags=["statistics"])
app.include_router(logs.router, prefix="/api", tags=["logs"])

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"ok": True, "message": "智能喂鸟器云端管理平台 API", "version": "1.0.0"}
