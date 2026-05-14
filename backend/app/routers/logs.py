from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_device_by_key, get_device_logs, create_device_log
from app.schemas import DeviceLogCreate

router = APIRouter()

def authenticate_device(x_device_key: str = Header(...), db: Session = Depends(get_db)):
    device = get_device_by_key(db, x_device_key)
    if not device:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的设备密钥")
    return device

@router.get("/device/logs")
async def get_logs(
    device_id: str = None,
    type: str = None,
    db: Session = Depends(get_db)
):
    logs = get_device_logs(db, device_id, type)
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "device_id": log.device_id,
            "type": log.type,
            "message": log.message,
            "created_at": log.created_at
        })
    return {"ok": True, "message": "success", "data": {"logs": result}}

@router.post("/device/logs")
async def upload_log(
    data: DeviceLogCreate,
    x_device_key: str = Header(...),
    db: Session = Depends(get_db)
):
    device = authenticate_device(x_device_key, db)
    if device.device_id != data.device_id:
        return {"ok": False, "message": "设备ID与密钥不匹配", "data": None}
    
    if data.type not in ["INFO", "WARNING", "ERROR"]:
        return {"ok": False, "message": "无效的日志类型", "data": None}
    
    log = create_device_log(db, data.device_id, data.type, data.message)
    return {
        "ok": True,
        "message": "日志上传成功",
        "data": {
            "id": log.id,
            "device_id": log.device_id,
            "type": log.type,
            "message": log.message,
            "created_at": log.created_at
        }
    }
