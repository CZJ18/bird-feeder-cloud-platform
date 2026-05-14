from pydantic import BaseModel
from typing import Optional, List

class DeviceHeartbeat(BaseModel):
    device_id: str
    battery: int
    food_level: int
    network: str
    status: str

class BirdEventCreate(BaseModel):
    device_id: str
    bird_name: str
    confidence: float
    battery: int
    food_level: int
    location: str

class DeviceCommandCreate(BaseModel):
    device_id: str
    command: str

class DeviceConfigUpdate(BaseModel):
    capture_interval: int
    confidence_threshold: float
    upload_image: bool
    night_mode: bool
    low_battery_threshold: int

class DeviceLogCreate(BaseModel):
    device_id: str
    type: str
    message: str

class HistoryQuery(BaseModel):
    device_id: Optional[str] = None
    bird_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    page: int = 1
    page_size: int = 10

class LogQuery(BaseModel):
    device_id: Optional[str] = None
    type: Optional[str] = None

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    name: str
    location: str
    status: str
    battery: int
    food_level: int
    network: str
    last_online: str
    created_at: str

class BirdEventResponse(BaseModel):
    id: int
    device_id: str
    bird_name: str
    confidence: float
    image_url: str
    location: str
    battery: int
    food_level: int
    created_at: str

class DeviceConfigResponse(BaseModel):
    device_id: str
    capture_interval: int
    confidence_threshold: float
    upload_image: bool
    night_mode: bool
    low_battery_threshold: int
    updated_at: str

class DeviceCommandResponse(BaseModel):
    id: int
    device_id: str
    command: str
    status: str
    created_at: str
    executed_at: Optional[str] = None

class DeviceLogResponse(BaseModel):
    id: int
    device_id: str
    type: str
    message: str
    created_at: str

class HistorySummary(BaseModel):
    total_count: int
    species_count: int
    today_count: int
    avg_confidence: float

class HistoryResponse(BaseModel):
    total: int
    records: List[BirdEventResponse]
    summary: HistorySummary

class StatisticsResponse(BaseModel):
    daily_counts: List[dict]
    species_counts: List[dict]
    device_upload_counts: List[dict]
    food_level_trend: List[dict]

class ApiResponse(BaseModel):
    ok: bool
    message: str
    data: Optional[dict] = None
