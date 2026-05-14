from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import (
    get_device_by_key, update_device_heartbeat, get_all_devices,
    get_device_config, create_or_update_device_config, create_device_command,
    get_pending_command, update_command_status
)
from app.schemas import (
    DeviceHeartbeat, DeviceCommandCreate, DeviceConfigUpdate,
    DeviceResponse, DeviceConfigResponse, DeviceCommandResponse
)

router = APIRouter()

def authenticate_device(x_device_key: str = Header(...), db: Session = Depends(get_db)):
    device = get_device_by_key(db, x_device_key)
    if not device:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的设备密钥")
    return device

@router.post("/device/heartbeat")
async def device_heartbeat(
    data: DeviceHeartbeat,
    x_device_key: str = Header(...),
    db: Session = Depends(get_db)
):
    device = authenticate_device(x_device_key, db)
    if device.device_id != data.device_id:
        return {"ok": False, "message": "设备ID与密钥不匹配", "data": None}
    
    updated_device = update_device_heartbeat(
        db, data.device_id, data.battery, data.food_level, data.network, data.status
    )
    
    return {
        "ok": True,
        "message": "心跳更新成功",
        "data": {
            "device_id": updated_device.device_id,
            "status": updated_device.status,
            "last_online": updated_device.last_online
        }
    }

@router.get("/device/list")
async def get_device_list(db: Session = Depends(get_db)):
    devices = get_all_devices(db)
    result = []
    for device in devices:
        result.append({
            "id": device.id,
            "device_id": device.device_id,
            "name": device.name,
            "location": device.location,
            "status": device.status,
            "battery": device.battery,
            "food_level": device.food_level,
            "network": device.network,
            "last_online": device.last_online,
            "created_at": device.created_at
        })
    return {"ok": True, "message": "success", "data": {"devices": result}}

@router.get("/device/config/{device_id}")
async def get_config(device_id: str, db: Session = Depends(get_db)):
    config = get_device_config(db, device_id)
    if config:
        return {
            "ok": True,
            "message": "success",
            "data": {
                "device_id": config.device_id,
                "capture_interval": config.capture_interval,
                "confidence_threshold": config.confidence_threshold,
                "upload_image": config.upload_image,
                "night_mode": config.night_mode,
                "low_battery_threshold": config.low_battery_threshold,
                "updated_at": config.updated_at
            }
        }
    else:
        return {
            "ok": True,
            "message": "使用默认配置",
            "data": {
                "device_id": device_id,
                "capture_interval": 300,
                "confidence_threshold": 0.85,
                "upload_image": True,
                "night_mode": True,
                "low_battery_threshold": 20,
                "updated_at": None
            }
        }

@router.post("/device/config/{device_id}")
async def save_config(
    device_id: str,
    data: DeviceConfigUpdate,
    db: Session = Depends(get_db)
):
    config = create_or_update_device_config(
        db, device_id, data.capture_interval, data.confidence_threshold,
        data.upload_image, data.night_mode, data.low_battery_threshold
    )
    return {
        "ok": True,
        "message": "配置保存成功",
        "data": {
            "device_id": config.device_id,
            "capture_interval": config.capture_interval,
            "confidence_threshold": config.confidence_threshold,
            "upload_image": config.upload_image,
            "night_mode": config.night_mode,
            "low_battery_threshold": config.low_battery_threshold,
            "updated_at": config.updated_at
        }
    }

@router.post("/device/command")
async def send_command(data: DeviceCommandCreate, db: Session = Depends(get_db)):
    if data.command not in ["take_photo", "restart"]:
        return {"ok": False, "message": "无效的命令", "data": None}
    
    device = get_device_by_key(db, "123456")
    if not device:
        return {"ok": False, "message": "设备不存在", "data": None}
    
    cmd = create_device_command(db, data.device_id, data.command)
    return {
        "ok": True,
        "message": "命令已下发",
        "data": {
            "id": cmd.id,
            "device_id": cmd.device_id,
            "command": cmd.command,
            "status": cmd.status,
            "created_at": cmd.created_at
        }
    }

@router.get("/device/command/{device_id}")
async def poll_command(
    device_id: str,
    x_device_key: str = Header(...),
    db: Session = Depends(get_db)
):
    device = authenticate_device(x_device_key, db)
    if device.device_id != device_id:
        return {"ok": False, "message": "设备ID与密钥不匹配", "data": None}
    
    cmd = get_pending_command(db, device_id)
    if cmd:
        return {
            "ok": True,
            "message": "success",
            "data": {
                "id": cmd.id,
                "device_id": cmd.device_id,
                "command": cmd.command,
                "status": cmd.status,
                "created_at": cmd.created_at
            }
        }
    else:
        return {"ok": True, "message": "暂无命令", "data": {"command": None}}

@router.post("/device/command/{command_id}/done")
async def command_done(
    command_id: int,
    x_device_key: str = Header(...),
    db: Session = Depends(get_db)
):
    authenticate_device(x_device_key, db)
    
    cmd = update_command_status(db, command_id, "done")
    if cmd:
        return {
            "ok": True,
            "message": "命令已完成",
            "data": {
                "id": cmd.id,
                "command": cmd.command,
                "status": cmd.status,
                "executed_at": cmd.executed_at
            }
        }
    else:
        return {"ok": False, "message": "命令不存在", "data": None}
