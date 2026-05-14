from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

db_path = os.getenv("SQLITE_DB_PATH", "./app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import Base, Device, DeviceConfig, BirdEvent, DeviceLog
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    if not db.query(Device).filter(Device.device_id == "bird_001").first():
        default_config = DeviceConfig(
            capture_interval=300,
            confidence_threshold=0.85,
            upload_image=True,
            night_mode=True,
            low_battery_threshold=20
        )
        test_device = Device(
            device_id="bird_001",
            name="一号智能喂鸟器",
            location="校园树林",
            status="online",
            battery=85,
            food_level=72,
            network="4G",
            last_online="2026-05-14 10:30:00",
            device_key="123456",
            config=default_config
        )
        db.add(test_device)
        
        mock_events = [
            {"bird_name": "麻雀", "confidence": 0.96, "battery": 85, "food_level": 72},
            {"bird_name": "燕子", "confidence": 0.89, "battery": 84, "food_level": 70},
            {"bird_name": "鸽子", "confidence": 0.92, "battery": 83, "food_level": 68},
            {"bird_name": "画眉", "confidence": 0.91, "battery": 82, "food_level": 66},
            {"bird_name": "斑鸠", "confidence": 0.88, "battery": 81, "food_level": 64},
            {"bird_name": "翠鸟", "confidence": 0.93, "battery": 80, "food_level": 62},
            {"bird_name": "啄木鸟", "confidence": 0.85, "battery": 79, "food_level": 60},
            {"bird_name": "喜鹊", "confidence": 0.90, "battery": 78, "food_level": 58},
        ]
        
        from datetime import datetime, timedelta
        for i, event in enumerate(mock_events):
            created_at = (datetime.now() - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
            bird_event = BirdEvent(
                device_id="bird_001",
                bird_name=event["bird_name"],
                confidence=event["confidence"],
                image_url=f"/uploads/bird_001/mock_{i}.jpg",
                location="校园树林",
                battery=event["battery"],
                food_level=event["food_level"],
                created_at=created_at
            )
            db.add(bird_event)
        
        mock_logs = [
            {"type": "INFO", "message": "设备上线"},
            {"type": "INFO", "message": "识别到鸟类: 麻雀, 置信度: 0.96"},
            {"type": "INFO", "message": "图片上传成功"},
            {"type": "WARNING", "message": "饲料余量低于35%"},
            {"type": "INFO", "message": "识别到鸟类: 燕子, 置信度: 0.89"},
            {"type": "INFO", "message": "心跳正常"},
        ]
        
        for i, log in enumerate(mock_logs):
            created_at = (datetime.now() - timedelta(minutes=i*30)).strftime("%Y-%m-%d %H:%M:%S")
            device_log = DeviceLog(
                device_id="bird_001",
                type=log["type"],
                message=log["message"],
                created_at=created_at
            )
            db.add(device_log)
        
        db.commit()
        print("初始化测试数据完成")
    
    db.close()
