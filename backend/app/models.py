from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    status = Column(String)
    battery = Column(Integer)
    food_level = Column(Integer)
    network = Column(String)
    last_online = Column(String)
    device_key = Column(String)
    created_at = Column(String)
    
    config = relationship("DeviceConfig", uselist=False, back_populates="device")
    events = relationship("BirdEvent", back_populates="device")
    commands = relationship("DeviceCommand", back_populates="device")
    logs = relationship("DeviceLog", back_populates="device")

class DeviceConfig(Base):
    __tablename__ = "device_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"), unique=True)
    capture_interval = Column(Integer)
    confidence_threshold = Column(Float)
    upload_image = Column(Boolean)
    night_mode = Column(Boolean)
    low_battery_threshold = Column(Integer)
    updated_at = Column(String)
    
    device = relationship("Device", back_populates="config")

class BirdEvent(Base):
    __tablename__ = "bird_events"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    bird_name = Column(String)
    confidence = Column(Float)
    image_url = Column(String)
    location = Column(String)
    battery = Column(Integer)
    food_level = Column(Integer)
    created_at = Column(String)
    
    device = relationship("Device", back_populates="events")

class DeviceCommand(Base):
    __tablename__ = "device_commands"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    command = Column(String)
    status = Column(String)
    created_at = Column(String)
    executed_at = Column(String)
    
    device = relationship("Device", back_populates="commands")

class DeviceLog(Base):
    __tablename__ = "device_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    type = Column(String)
    message = Column(String)
    created_at = Column(String)
    
    device = relationship("Device", back_populates="logs")
