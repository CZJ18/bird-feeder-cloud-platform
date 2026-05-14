from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.models import Device, DeviceConfig, BirdEvent, DeviceCommand, DeviceLog
from datetime import datetime, timedelta
import os

def get_device_by_id(db: Session, device_id: str):
    return db.query(Device).filter(Device.device_id == device_id).first()

def get_device_by_key(db: Session, device_key: str):
    return db.query(Device).filter(Device.device_key == device_key).first()

def get_all_devices(db: Session):
    return db.query(Device).all()

def update_device_heartbeat(db: Session, device_id: str, battery: int, food_level: int, network: str, status: str):
    device = get_device_by_id(db, device_id)
    if device:
        device.battery = battery
        device.food_level = food_level
        device.network = network
        device.status = status
        device.last_online = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()
        db.refresh(device)
    return device

def create_bird_event(db: Session, device_id: str, bird_name: str, confidence: float, image_url: str, location: str, battery: int, food_level: int):
    event = BirdEvent(
        device_id=device_id,
        bird_name=bird_name,
        confidence=confidence,
        image_url=image_url,
        location=location,
        battery=battery,
        food_level=food_level,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_recent_events(db: Session, limit: int = 20):
    return db.query(BirdEvent).order_by(desc(BirdEvent.created_at)).limit(limit).all()

def get_history_events(db: Session, device_id=None, bird_name=None, start_time=None, end_time=None, 
                       min_confidence=None, max_confidence=None, page=1, page_size=10):
    query = db.query(BirdEvent)
    
    if device_id:
        query = query.filter(BirdEvent.device_id == device_id)
    if bird_name:
        query = query.filter(BirdEvent.bird_name.like(f"%{bird_name}%"))
    if start_time:
        query = query.filter(BirdEvent.created_at >= start_time)
    if end_time:
        query = query.filter(BirdEvent.created_at <= end_time)
    if min_confidence is not None:
        query = query.filter(BirdEvent.confidence >= min_confidence)
    if max_confidence is not None:
        query = query.filter(BirdEvent.confidence <= max_confidence)
    
    total = query.count()
    records = query.order_by(desc(BirdEvent.created_at)).offset((page-1)*page_size).limit(page_size).all()
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_query = db.query(BirdEvent).filter(BirdEvent.created_at.like(f"{today}%"))
    if device_id:
        today_query = today_query.filter(BirdEvent.device_id == device_id)
    today_count = today_query.count()
    
    all_records_query = db.query(BirdEvent)
    if device_id:
        all_records_query = all_records_query.filter(BirdEvent.device_id == device_id)
    total_count = all_records_query.count()
    
    species_query = db.query(func.distinct(BirdEvent.bird_name))
    if device_id:
        species_query = species_query.filter(BirdEvent.device_id == device_id)
    species_count = species_query.count()
    
    avg_conf_query = db.query(func.avg(BirdEvent.confidence))
    if device_id:
        avg_conf_query = avg_conf_query.filter(BirdEvent.device_id == device_id)
    avg_confidence = avg_conf_query.scalar() or 0.0
    
    return {
        "total": total,
        "records": records,
        "summary": {
            "total_count": total_count,
            "species_count": species_count,
            "today_count": today_count,
            "avg_confidence": round(avg_confidence, 2)
        }
    }

def get_device_config(db: Session, device_id: str):
    return db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id).first()

def create_or_update_device_config(db: Session, device_id: str, capture_interval: int, 
                                   confidence_threshold: float, upload_image: bool, 
                                   night_mode: bool, low_battery_threshold: int):
    config = get_device_config(db, device_id)
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if config:
        config.capture_interval = capture_interval
        config.confidence_threshold = confidence_threshold
        config.upload_image = upload_image
        config.night_mode = night_mode
        config.low_battery_threshold = low_battery_threshold
        config.updated_at = updated_at
    else:
        config = DeviceConfig(
            device_id=device_id,
            capture_interval=capture_interval,
            confidence_threshold=confidence_threshold,
            upload_image=upload_image,
            night_mode=night_mode,
            low_battery_threshold=low_battery_threshold,
            updated_at=updated_at
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    return config

def create_device_command(db: Session, device_id: str, command: str):
    cmd = DeviceCommand(
        device_id=device_id,
        command=command,
        status="pending",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return cmd

def get_pending_command(db: Session, device_id: str):
    return db.query(DeviceCommand).filter(
        DeviceCommand.device_id == device_id,
        DeviceCommand.status == "pending"
    ).order_by(desc(DeviceCommand.created_at)).first()

def update_command_status(db: Session, command_id: int, status: str):
    cmd = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
    if cmd:
        cmd.status = status
        cmd.executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()
        db.refresh(cmd)
    return cmd

def get_device_logs(db: Session, device_id=None, log_type=None):
    query = db.query(DeviceLog).order_by(desc(DeviceLog.created_at))
    
    if device_id:
        query = query.filter(DeviceLog.device_id == device_id)
    if log_type:
        query = query.filter(DeviceLog.type == log_type)
    
    return query.all()

def create_device_log(db: Session, device_id: str, log_type: str, message: str):
    log = DeviceLog(
        device_id=device_id,
        type=log_type,
        message=message,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_statistics(db: Session):
    today = datetime.now()
    
    daily_counts = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        count = db.query(BirdEvent).filter(BirdEvent.created_at.like(f"{date}%")).count()
        daily_counts.append({"date": date, "count": count})
    daily_counts.reverse()
    
    species_counts = []
    species_query = db.query(BirdEvent.bird_name, func.count(BirdEvent.id)).group_by(BirdEvent.bird_name).order_by(desc(func.count(BirdEvent.id)))
    for species, count in species_query.all():
        species_counts.append({"name": species, "count": count})
    
    device_upload_counts = []
    device_query = db.query(Device.device_id, Device.name, func.count(BirdEvent.id)).outerjoin(BirdEvent).group_by(Device.device_id, Device.name).order_by(desc(func.count(BirdEvent.id)))
    for device_id, name, count in device_query.all():
        device_upload_counts.append({"device_id": device_id, "device_name": name, "upload_count": count or 0})
    
    food_level_trend = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        avg_food = db.query(func.avg(BirdEvent.food_level)).filter(BirdEvent.created_at.like(f"{date}%")).scalar()
        food_level_trend.append({"date": date, "food_level": round(avg_food or 50)})
    food_level_trend.reverse()
    
    return {
        "daily_counts": daily_counts,
        "species_counts": species_counts,
        "device_upload_counts": device_upload_counts,
        "food_level_trend": food_level_trend
    }
