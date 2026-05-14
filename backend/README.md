# 智能喂鸟器云端管理平台 - 后端服务

## 技术栈

- Python 3.8+
- FastAPI
- SQLite
- SQLAlchemy

## 功能特性

- 设备心跳管理
- 鸟类识别结果上传
- 设备配置管理
- 远程命令下发
- 系统日志管理
- 统计数据查询

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 启动服务

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

服务启动后访问: http://localhost:8080

## 接口文档

启动服务后访问:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 测试设备信息

- device_id: bird_001
- device_key: 123456
- name: 一号智能喂鸟器
- location: 校园树林

## 接口测试方法

### 1. 设备心跳

```bash
curl -X POST http://localhost:8080/api/device/heartbeat \
  -H "Content-Type: application/json" \
  -H "X-Device-Key: 123456" \
  -d '{"device_id": "bird_001", "battery": 85, "food_level": 72, "network": "4G", "status": "online"}'
```

### 2. 上传识别结果

```bash
curl -X POST http://localhost:8080/api/bird/event \
  -H "X-Device-Key: 123456" \
  -F "device_id=bird_001" \
  -F "bird_name=麻雀" \
  -F "confidence=0.96" \
  -F "battery=85" \
  -F "food_level=72" \
  -F "location=校园树林" \
  -F "image=@test.jpg"
```

### 3. 获取设备列表

```bash
curl http://localhost:8080/api/device/list
```

### 4. 获取最近识别记录

```bash
curl http://localhost:8080/api/bird/events
```

### 5. 获取历史记录

```bash
curl "http://localhost:8080/api/bird/history?page=1&page_size=10"
```

### 6. 获取统计数据

```bash
curl http://localhost:8080/api/statistics
```

### 7. 获取设备配置

```bash
curl http://localhost:8080/api/device/config/bird_001
```

### 8. 保存设备配置

```bash
curl -X POST http://localhost:8080/api/device/config/bird_001 \
  -H "Content-Type: application/json" \
  -d '{
    "capture_interval": 300,
    "confidence_threshold": 0.85,
    "upload_image": true,
    "night_mode": true,
    "low_battery_threshold": 20
  }'
```

### 9. 下发设备命令

```bash
curl -X POST http://localhost:8080/api/device/command \
  -H "Content-Type: application/json" \
  -d '{"device_id": "bird_001", "command": "take_photo"}'
```

### 10. 设备轮询命令

```bash
curl -X GET http://localhost:8080/api/device/command/bird_001 \
  -H "X-Device-Key: 123456"
```

### 11. 命令执行完成

```bash
curl -X POST http://localhost:8080/api/device/command/1/done \
  -H "X-Device-Key: 123456"
```

### 12. 获取设备日志

```bash
curl "http://localhost:8080/api/device/logs?device_id=bird_001"
```

### 13. 设备上传日志

```bash
curl -X POST http://localhost:8080/api/device/logs \
  -H "Content-Type: application/json" \
  -H "X-Device-Key: 123456" \
  -d '{"device_id": "bird_001", "type": "INFO", "message": "测试日志"}'
```

## 项目结构

```
backend/
├── app/
│   ├── main.py          # 主入口
│   ├── database.py      # 数据库配置
│   ├── models.py        # 数据模型
│   ├── schemas.py       # 数据结构定义
│   ├── crud.py          # 数据库操作
│   ├── config.py        # 配置文件
│   └── routers/         # 路由模块
│       ├── device.py    # 设备相关接口
│       ├── bird.py      # 鸟类识别接口
│       ├── statistics.py # 统计数据接口
│       └── logs.py      # 日志接口
├── uploads/             # 图片上传目录
├── requirements.txt     # 依赖列表
└── README.md           # 项目说明
```

## 数据库表结构

### devices 设备表
- id, device_id, name, location, status, battery, food_level, network, last_online, device_key, created_at

### bird_events 鸟类识别记录表
- id, device_id, bird_name, confidence, image_url, location, battery, food_level, created_at

### device_configs 设备配置表
- id, device_id, capture_interval, confidence_threshold, upload_image, night_mode, low_battery_threshold, updated_at

### device_commands 设备命令表
- id, device_id, command, status, created_at, executed_at

### device_logs 日志表
- id, device_id, type, message, created_at
