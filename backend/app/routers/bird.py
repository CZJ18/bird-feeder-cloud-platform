from fastapi import APIRouter, Depends, Header, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_device_by_key, create_bird_event, get_recent_events, get_history_events
from app.config import MAX_FILE_SIZE, UPLOAD_DIR, allowed_file, get_file_extension
import os
import shutil
from datetime import datetime

router = APIRouter()

def authenticate_device(x_device_key: str = Header(...), db: Session = Depends(get_db)):
    device = get_device_by_key(db, x_device_key)
    if not device:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的设备密钥")
    return device

@router.post("/bird/event")
async def upload_bird_event(
    device_id: str,
    bird_name: str,
    confidence: float,
    battery: int,
    food_level: int,
    location: str,
    image: UploadFile = File(...),
    x_device_key: str = Header(...),
    db: Session = Depends(get_db)
):
    device = authenticate_device(x_device_key, db)
    if device.device_id != device_id:
        return {"ok": False, "message": "设备ID与密钥不匹配", "data": None}
    
    if not allowed_file(image.filename):
        return {"ok": False, "message": "不支持的图片格式", "data": None}
    
    file_size = 0
    chunk = await image.read(MAX_FILE_SIZE + 1)
    file_size = len(chunk)
    if file_size > MAX_FILE_SIZE:
        return {"ok": False, "message": "文件大小超过限制", "data": None}
    
    upload_dir = os.path.join(UPLOAD_DIR, device_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.{get_file_extension(image.filename)}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(chunk)
    
    image_url = f"/uploads/{device_id}/{filename}"
    
    event = create_bird_event(db, device_id, bird_name, confidence, image_url, location, battery, food_level)
    
    return {
        "ok": True,
        "message": "识别结果上传成功",
        "data": {
            "id": event.id,
            "device_id": event.device_id,
            "bird_name": event.bird_name,
            "confidence": event.confidence,
            "image_url": event.image_url,
            "created_at": event.created_at
        }
    }

@router.get("/bird/events")
async def get_recent_bird_events(db: Session = Depends(get_db)):
    events = get_recent_events(db)
    result = []
    for event in events:
        result.append({
            "id": event.id,
            "device_id": event.device_id,
            "bird_name": event.bird_name,
            "confidence": event.confidence,
            "image_url": event.image_url,
            "location": event.location,
            "battery": event.battery,
            "food_level": event.food_level,
            "created_at": event.created_at
        })
    return {"ok": True, "message": "success", "data": {"events": result}}

@router.get("/bird/history")
async def get_bird_history(
    device_id: str = None,
    bird_name: str = None,
    start_time: str = None,
    end_time: str = None,
    min_confidence: float = None,
    max_confidence: float = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    result = get_history_events(db, device_id, bird_name, start_time, end_time, min_confidence, max_confidence, page, page_size)
    
    records = []
    for record in result["records"]:
        records.append({
            "id": record.id,
            "device_id": record.device_id,
            "bird_name": record.bird_name,
            "confidence": record.confidence,
            "image_url": record.image_url,
            "location": record.location,
            "battery": record.battery,
            "food_level": record.food_level,
            "created_at": record.created_at
        })
    
    return {
        "ok": True,
        "message": "success",
        "data": {
            "total": result["total"],
            "records": records,
            "summary": result["summary"]
        }
    }
