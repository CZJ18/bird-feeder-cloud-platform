# 鸟类智能监测系统后端需求规格文档

文档版本：1.0  
目标后端技术栈：FastAPI + Tortoise-ORM + MySQL + aiomqtt  
适用范围：鸟类智能监测大屏、设备状态监控、边缘设备图片上报、MQTT 事件消费与入库。

## 1. 项目目标

后端需要为鸟类智能监测系统提供统一的数据服务，主要承担以下职责：

- 接收边缘设备通过 MQTT 上报的高置信度识别事件和设备状态。
- 接收边缘设备通过 HTTP multipart 上传的低置信度图片。
- 为前端大屏提供统计、趋势、地图、设备状态、精彩瞬间、低置信度审核等接口。
- 使用 MySQL 做持久化存储，使用 Tortoise-ORM 完成异步数据库访问。
- 使用静态 Token 保护前端大屏接口，使用设备 API Key 保护边缘设备上传接口。

## 2. 技术栈

后端必须使用以下技术栈：

| 类型 | 技术 |
| --- | --- |
| Web 框架 | FastAPI |
| ORM | Tortoise-ORM |
| 数据库 | MySQL |
| MQTT 客户端 | aiomqtt |
| ASGI 服务 | uvicorn |
| 配置管理 | python-dotenv / pydantic settings |
| 日志 | loguru |
| 文件上传 | python-multipart |
| 数据迁移 | aerich |

`requirements.txt` 至少包含：

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
tortoise-orm==0.20.0
aiomysql==0.2.0
aiomqtt==2.0.0
pydantic==2.8.0
python-dotenv==1.0.0
aerich==0.7.2
loguru==0.7.2
python-multipart==0.0.9
```

## 3. 推荐目录结构

```txt
birdcam_project/
├── frontend/                         # 已有前端项目
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   ├── README.md
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 应用、生命周期、路由注册
│   │   ├── config.py                 # 环境变量配置
│   │   ├── database.py               # Tortoise 初始化、关闭、迁移配置
│   │   ├── models.py                 # 数据库模型
│   │   ├── dependencies.py           # API Token、设备 API Key 校验依赖
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # 汇总所有 API router
│   │   │   ├── dashboard.py          # 大屏核心指标
│   │   │   ├── species.py            # 物种分布
│   │   │   ├── time_dynamics.py      # 时间动态
│   │   │   ├── monthly_trend.py      # 月度趋势
│   │   │   ├── devices.py            # 设备状态、地图、配置
│   │   │   ├── moments.py            # 精彩瞬间
│   │   │   ├── low_confidence.py     # 低置信度审核
│   │   │   ├── events.py             # 识别事件兼容接口
│   │   │   ├── logs.py               # 系统日志
│   │   │   └── upload.py             # POST /upload
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── dashboard.py
│   │   │   ├── device.py
│   │   │   ├── event.py
│   │   │   ├── low_confidence.py
│   │   │   └── moment.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── statistics.py
│   │   │   ├── device_service.py
│   │   │   ├── event_service.py
│   │   │   ├── upload_service.py
│   │   │   └── mqtt_handler.py
│   │   ├── mqtt_client/
│   │   │   ├── __init__.py
│   │   │   └── consumer.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py
│   │   │   ├── time_utils.py
│   │   │   └── logger.py
│   │   └── static/
│   │       └── uploads/
│   │           └── low_confidence/
│   ├── scripts/
│   │   ├── init_db.py
│   │   ├── seed_species.py
│   │   ├── seed_devices.py
│   │   └── dev_run.bat
│   ├── tests/
│   └── logs/
└── README.md
```

## 4. 环境变量

`.env.example` 必须包含：

```ini
# MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=birdcam_user
DB_PASSWORD=change_me
DB_NAME=birdcam_db

# MQTT
MQTT_HOST=127.0.0.1
MQTT_PORT=8883
MQTT_USER=mqtt_user
MQTT_PASSWORD=mqtt_pass
MQTT_TLS_CA_PATH=./certs/ca.crt
MQTT_TOPIC_EVENT=birdcam/event
MQTT_TOPIC_STATUS=birdcam/status
MQTT_RECONNECT_INTERVAL_SECONDS=5

# 文件存储
UPLOAD_BASE_DIR=./app/static/uploads/low_confidence
UPLOAD_PUBLIC_PREFIX=/uploads/low_confidence
MAX_UPLOAD_SIZE_MB=10

# API 安全
DASHBOARD_API_TOKEN=change_me_to_a_long_random_token
DEVICE_API_KEY_LENGTH=64

# 在线判定
DEVICE_ONLINE_SECONDS=300

# 服务
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

## 5. 数据库模型

所有模型必须继承 Tortoise `Model`，所有时间字段统一使用 UTC 或服务端配置时区，API 输出使用 ISO 8601 字符串。

### 5.1 Device 设备表

表名：`devices`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Int | pk | 自增主键 |
| device_id | Char(64) | unique, not null | 边缘设备标识，例如 `birdcam_layer8` |
| name | Char(64) | null | 前端展示名称 |
| api_key | Char(128) | unique, not null | 设备独立 API Key，用于 `/upload` |
| latitude | Decimal(10,7) | null | 纬度 |
| longitude | Decimal(10,7) | null | 经度 |
| location_desc | Char(255) | null | 位置描述 |
| install_date | Date | null | 安装日期 |
| status | Int | default=1 | 1 启用，0 停用 |
| created_at | Datetime | auto_now_add | 创建时间 |
| updated_at | Datetime | auto_now | 更新时间 |

索引：

- `device_id` 唯一索引。
- `api_key` 唯一索引。
- `status` 普通索引。

### 5.2 SpeciesDict 物种字典

表名：`species_dict`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| class_id | Int | pk | 边缘模型类别 ID，0 到 17 |
| species_en | Char(96) | not null | 英文名 |
| species_cn | Char(64) | not null | 中文名 |
| created_at | Datetime | auto_now_add | 创建时间 |

### 5.3 EventLeave 高置信度离开事件

表名：`event_leave`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BigInt | pk | 自增主键 |
| track_id | Int | not null | 跟踪 ID |
| device | ForeignKey(Device) | not null | 设备 |
| timestamp | Datetime | index, not null | 事件时间 |
| confidence | Decimal(5,4) | not null | 置信度，0 到 1 |
| box_x1 | Decimal(8,2) | not null | 检测框 x1 |
| box_y1 | Decimal(8,2) | not null | 检测框 y1 |
| box_x2 | Decimal(8,2) | not null | 检测框 x2 |
| box_y2 | Decimal(8,2) | not null | 检测框 y2 |
| species | ForeignKey(SpeciesDict) | null | 物种 |
| species_name | Char(64) | null | 冗余中文名 |
| video_path | Char(512) | null | 关联视频地址或路径 |
| raw_payload | JSON | null | 原始 MQTT 数据，便于排查 |
| created_at | Datetime | auto_now_add | 入库时间 |

索引：

- `(device_id, timestamp)`。
- `(species_id, timestamp)`。
- `timestamp`。

### 5.4 DeviceStatus 设备状态历史

表名：`device_status`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BigInt | pk | 自增主键 |
| device | ForeignKey(Device) | not null | 设备 |
| timestamp | Datetime | index, not null | 状态上报时间 |
| cpu_temperature | Decimal(5,2) | null | CPU 温度 |
| mem_total_mb | Decimal(10,2) | null | 内存总量 |
| mem_available_mb | Decimal(10,2) | null | 可用内存 |
| mem_percent | Decimal(5,2) | null | 内存使用率 |
| disk_total_gb | Decimal(10,2) | null | 磁盘总量 |
| disk_free_gb | Decimal(10,2) | null | 磁盘剩余 |
| disk_percent | Decimal(5,2) | null | 磁盘使用率 |
| battery | Int | null | 电量百分比，兼容前端管理端 |
| food_level | Int | null | 饲料余量百分比，兼容前端管理端 |
| network | Char(32) | null | 4G/WiFi/Ethernet |
| raw_payload | JSON | null | 原始 MQTT 数据 |
| created_at | Datetime | auto_now_add | 入库时间 |

索引：

- `(device_id, timestamp)`。
- `timestamp`。

### 5.5 LowConfidenceImage 低置信度图片

表名：`low_confidence_images`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BigInt | pk | 自增主键 |
| device | ForeignKey(Device) | not null | 设备 |
| timestamp | Datetime | index, not null | 图片产生时间 |
| confidence | Decimal(5,4) | not null | 置信度 |
| species | ForeignKey(SpeciesDict) | null | 初始识别物种 |
| species_name | Char(64) | null | 冗余中文名 |
| box_x1 | Decimal(8,2) | not null | 检测框 x1 |
| box_y1 | Decimal(8,2) | not null | 检测框 y1 |
| box_x2 | Decimal(8,2) | not null | 检测框 x2 |
| box_y2 | Decimal(8,2) | not null | 检测框 y2 |
| rule_triggered | Char(128) | null | 边缘规则名 |
| image_path | Char(512) | not null | 服务端存储路径 |
| image_url | Char(512) | not null | 前端可访问 URL |
| review_status | Char(16) | default=pending | pending/approved/rejected |
| review_comment | Char(255) | null | 审核备注 |
| reviewed_at | Datetime | null | 审核时间 |
| raw_payload | JSON | null | 表单元数据 |
| created_at | Datetime | auto_now_add | 入库时间 |

索引：

- `review_status`。
- `(device_id, timestamp)`。
- `(review_status, timestamp)`。

### 5.6 Moment 精彩瞬间

表名：`moments`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Int | pk | 自增主键 |
| event | ForeignKey(EventLeave) | null | 可关联高置信度事件 |
| title | Char(128) | not null | 标题 |
| video_url | Char(512) | not null | 视频 URL |
| cover_image | Char(512) | null | 封面图 |
| sort_order | Int | default=0 | 排序值 |
| is_active | Bool | default=true | 是否展示 |
| created_at | Datetime | auto_now_add | 创建时间 |
| updated_at | Datetime | auto_now | 更新时间 |

### 5.7 SystemLog 系统日志

表名：`system_logs`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BigInt | pk | 自增主键 |
| device | ForeignKey(Device) | null | 关联设备 |
| type | Char(16) | index | INFO/WARNING/ERROR |
| message | Char(512) | not null | 日志内容 |
| source | Char(32) | null | api/mqtt/upload/system |
| created_at | Datetime | auto_now_add | 创建时间 |

### 5.8 DeviceConfig 设备配置

表名：`device_configs`

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Int | pk | 自增主键 |
| device | OneToOne(Device) | unique | 设备 |
| capture_interval | Int | default=300 | 采集间隔，秒 |
| confidence_threshold | Decimal(5,4) | default=0.85 | 高置信度阈值 |
| upload_image | Bool | default=true | 是否上传图片 |
| night_mode | Bool | default=true | 夜间模式 |
| low_battery_threshold | Int | default=20 | 低电量阈值 |
| updated_at | Datetime | auto_now | 更新时间 |

## 6. 通用 API 规范

### 6.1 响应格式

前端大屏接口统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

为兼容已有管理前端，也允许返回：

```json
{
  "ok": true,
  "message": "success",
  "data": {}
}
```

建议新接口统一使用 `code/message/data`，兼容接口使用 `ok/message/data`。

### 6.2 错误格式

```json
{
  "code": 401,
  "message": "Unauthorized",
  "data": null
}
```

常用状态码：

| HTTP 状态码 | code | 场景 |
| --- | --- | --- |
| 200 | 200 | 成功 |
| 400 | 400 | 请求参数错误 |
| 401 | 401 | Token 或设备 API Key 无效 |
| 404 | 404 | 资源不存在 |
| 413 | 413 | 上传文件过大 |
| 500 | 500 | 服务端异常 |

### 6.3 前端大屏认证

所有 `/api/*` 接口必须校验请求头：

```http
X-API-Token: <DASHBOARD_API_TOKEN>
```

校验规则：

- 服务端从 `.env` 读取 `DASHBOARD_API_TOKEN`。
- 使用 `secrets.compare_digest` 做常量时间比较。
- 未携带、为空、错误均返回 401。
- `/upload` 不使用 `X-API-Token`，只使用设备 API Key。

## 7. 前端大屏 API 接口

### 7.0 大屏展示项计算口径与刷新间隔

| 前端展示字段 | 计算方式 | 推荐刷新间隔 |
| --- | --- | --- |
| 累计识别总数 | 统计 `EventLeave` 表中所有 `leave` 事件总数。 | 30 秒 |
| 累计物种数 | 统计 `EventLeave` 表中不同 `species_id` / `class_id` 的数量。 | 30 秒 |
| 在线设备数 | 查询 `DeviceStatus` 表，取最近 5 分钟内有状态上报的设备并去重计数。 | 5 分钟 |
| 今日新增 | 筛选今天发生的 `leave` 事件并统计数量。 | 30 秒 |
| 今日活跃设备 | 筛选今天有任意事件或状态上报的设备并去重计数。 | 1 分钟 |
| 待审核图片 | 统计 `LowConfidenceImage.review_status = "pending"` 的记录数。 | 手动刷新 |
| 平均置信度 | 计算 `EventLeave.confidence` 全量平均值，再乘以 100 并取整。 | 30 秒 |
| 今日观测物种数 | 从今天的 `leave` 事件中统计不同 `species_id` / `class_id` 数量。 | 30 秒 |
| 物种分布（饼图） | 按 `species_id` / `class_id` 分组统计事件数量，取前 N 名，并关联 `SpeciesDict` 得到中文名。 | 1 分钟 |
| 时间动态（折线图） | 按天/周/月聚合事件数量；同时间段温度取 `DeviceStatus.cpu_temperature` 平均值。 | 1 分钟 |
| 月度趋势（堆叠图） | 按年份和月份聚合事件数量，再按物种拆分。 | 页面加载 |
| 设备状态列表 | 每台设备取最新一条 `DeviceStatus`，最后上报时间在 5 分钟内判定为在线。 | 5 分钟 |
| 设备地图数据 | 按年份聚合每台设备事件数量，并从 `Device` 表读取经纬度。 | 页面加载 |
| 精彩瞬间 | 直接读取 `Moment` 表中 `is_active = true` 的记录。 | 页面加载 |
| 低置信度列表 | 从 `LowConfidenceImage` 表读取，按时间倒序排列。 | 手动刷新 |

### 7.1 GET `/api/dashboard/statistics`

用途：返回大屏顶部和核心 KPI。

认证：`X-API-Token`

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "speciesStats": {
      "totalVisits": 24835,
      "totalSpecies": 18,
      "onlineCount": 9
    },
    "kpiCard": {
      "todayNew": 372,
      "todayActive": 9,
      "pendingReview": 9,
      "avgConfidence": 86,
      "todaySpeciesCount": 8
    }
  }
}
```

字段计算规则：

- `totalVisits`：`EventLeave` 总数。
- `totalSpecies`：`EventLeave` 中实际出现过的不同 `species_id` / `class_id` 数量。
- `onlineCount`：最近 `DEVICE_ONLINE_SECONDS` 内有状态上报的设备数量。
- `todayNew`：当天高置信度事件数量。
- `todayActive`：当天有状态上报或事件上报的设备数量。
- `pendingReview`：`LowConfidenceImage.review_status = pending` 数量。
- `avgConfidence`：所有 `EventLeave.confidence` 平均值乘以 100 后取整。
- `todaySpeciesCount`：当天 `leave` 事件中不同 `species_id` / `class_id` 数量。

### 7.2 GET `/api/species/distribution`

用途：返回物种出现次数 TOP N，用于饼图、柱图。

认证：`X-API-Token`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| top | int | 10 | 返回前 N 个物种 |
| start_date | string | null | 起始日期，`YYYY-MM-DD` |
| end_date | string | null | 结束日期，`YYYY-MM-DD` |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "regionData": [
      { "name": "白鹭", "value": 1234 },
      { "name": "树麻雀", "value": 987 }
    ]
  }
}
```

### 7.3 GET `/api/time-dynamics`

用途：返回按天、周、月聚合的识别数量和温度数据。

认证：`X-API-Token`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| days | int | 7 | 最近天数 |
| unit | string | day | `day` / `week` / `month` |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "regionData": [
      { "id": 1, "mdate": "2025-03-31", "value": 50, "temperature": 28.5 }
    ]
  }
}
```

字段说明：

- `value`：该时间粒度下 `EventLeave` 数量。
- `temperature`：该时间粒度下设备 CPU 温度平均值；没有数据时返回 `null`。

### 7.4 GET `/api/monthly-trend`

用途：返回某年每个月各物种识别数量。

认证：`X-API-Token`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| year | int | 当前年份 | 统计年份 |
| top | int | 8 | 只返回出现次数前 N 的物种 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "dimensions": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
    "data": [
      { "species": "白鹭", "values": [56, 82, 31, 44, 91, 108, 76, 88, 65, 53, 47, 51] }
    ]
  }
}
```

### 7.5 GET `/api/devices/status`

用途：返回所有设备的最新状态。

认证：`X-API-Token`

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "devices": [
      {
        "device_id": "birdcam_layer8",
        "name": "大围山观测点1",
        "cpu_temperature": 48.5,
        "memory_usage": {
          "total_mb": 8192,
          "available_mb": 3200.5,
          "percent": 60.9
        },
        "disk_usage": {
          "total_gb": 128,
          "free_gb": 45.3,
          "percent": 64.6
        },
        "online": true,
        "last_seen": "2025-03-31T10:30:00"
      }
    ]
  }
}
```

`online` 判定规则：最新 `DeviceStatus.timestamp` 距离当前时间小于等于 `DEVICE_ONLINE_SECONDS`。

### 7.6 GET `/api/devices/map`

用途：返回地图可视化数据，按年份聚合设备识别数量。

认证：`X-API-Token`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| start_year | int | 当前年份 - 4 | 起始年份 |
| end_year | int | 当前年份 | 结束年份 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "voltageLevel": ["2021", "2022", "2023", "2024", "2025"],
    "categoryData": {
      "2025": [
        { "name": "大围山观测点1", "value": 100 }
      ]
    },
    "topData": {
      "2025": [
        { "name": "大围山观测点1", "value": [113.1234567, 28.1234567, 100] }
      ]
    },
    "colors": ["#1de9b6", "#f46e36", "#04b9ff", "#5dbd32", "#ffc809"]
  }
}
```

字段说明：

- `voltageLevel`：年份字符串数组，沿用前端模拟数据字段名。
- `categoryData[year]`：设备名称和该年份识别总数。
- `topData[year]`：设备名称、经度、纬度、识别总数。

### 7.7 GET `/api/moments`

用途：返回精彩瞬间视频列表。

认证：`X-API-Token`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| limit | int | 10 | 返回数量 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "regionData": [
      {
        "id": 1,
        "videoUrl": "https://example.com/videos/moment-1.mp4",
        "title": "白颊噪鹛晨间觅食",
        "coverImage": "https://example.com/covers/moment-1.jpg"
      }
    ]
  }
}
```

### 7.8 GET `/api/low-confidence`

用途：返回低置信度图片列表，供人工审核。

认证：`X-API-Token`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| page | int | 1 | 页码 |
| size | int | 10 | 每页数量 |
| status | string | pending | pending/approved/rejected/all |
| device_id | string | null | 设备筛选 |
| start_date | string | null | 起始日期 |
| end_date | string | null | 结束日期 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "list": [
      {
        "id": 1,
        "device": "大围山观测点1",
        "device_id": "birdcam_layer8",
        "species": "灰喜鹊",
        "confidence": 0.52,
        "timestamp": "2025-03-31T08:12:34",
        "image_url": "/uploads/low_confidence/20250331/birdcam_layer8_1743389554_abcd.jpg",
        "review_status": "pending"
      }
    ]
  }
}
```

### 7.9 PUT `/api/low-confidence/{id}`

用途：审核低置信度图片。

认证：`X-API-Token`

请求体：

```json
{
  "review_status": "approved",
  "review_comment": "确认为灰喜鹊"
}
```

规则：

- `review_status` 只能是 `approved` 或 `rejected`。
- 审核成功后更新 `reviewed_at`。
- 如果记录不存在，返回 404。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "review_status": "approved",
    "review_comment": "确认为灰喜鹊"
  }
}
```

## 8. 兼容当前前端管理端的接口

当前 Vue 管理端 mock 数据包含设备列表、识别记录、历史筛选、设备配置、日志、统计等结构。后端应额外提供以下兼容接口，避免前端继续回退到 Mock。

### 8.1 GET `/api/statistics`

响应：

```json
{
  "ok": true,
  "message": "success",
  "data": {
    "daily_counts": [
      { "date": "2026-05-14", "count": 128 }
    ],
    "species_counts": [
      { "name": "麻雀", "count": 320 }
    ],
    "device_upload_counts": [
      { "device_id": "BF-001", "device_name": "后山观鸟点1号", "upload_count": 1250 }
    ],
    "food_level_trend": [
      { "date": "2026-05-14", "food_level": 72 }
    ]
  }
}
```

### 8.2 GET `/api/device/list`

响应：

```json
{
  "ok": true,
  "message": "success",
  "data": {
    "devices": [
      {
        "device_id": "BF-001",
        "name": "后山观鸟点1号",
        "location": "后山林区",
        "status": "online",
        "battery": 85,
        "food_level": 72,
        "network": "4G",
        "last_online": "2026-05-14 10:30:00"
      }
    ]
  }
}
```

字段映射：

- `location` 来自 `Device.location_desc`。
- `status` 根据最新状态时间转换为 `online` / `offline`。
- `battery`、`food_level`、`network` 来自最新 `DeviceStatus`。

### 8.3 GET `/api/bird/events`

查询参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| device_id | string | null | 设备筛选 |
| bird_name | string | null | 鸟名模糊筛选 |
| limit | int | null | 返回数量 |

响应：

```json
{
  "ok": true,
  "message": "success",
  "data": {
    "events": [
      {
        "id": 1,
        "device_id": "BF-001",
        "bird_name": "麻雀",
        "confidence": 0.96,
        "image_url": "/uploads/low_confidence/20260514/demo.jpg",
        "battery": 85,
        "food_level": 72,
        "created_at": "2026-05-14 10:30:00"
      }
    ]
  }
}
```

数据来源：

- 优先返回 `EventLeave`，如无图片可返回关联视频封面或空图片。
- 低置信度图片审核通过后也可进入该列表，具体由产品口径决定。

### 8.4 GET `/api/bird/history`

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| device_id | string | 设备 ID |
| bird_name | string | 鸟类名称 |
| start_time | string | 起始时间 |
| end_time | string | 结束时间 |
| min_confidence | float | 最低置信度 |
| max_confidence | float | 最高置信度 |
| page | int | 页码，默认 1 |
| page_size | int | 每页数量，默认 10 |

响应：

```json
{
  "ok": true,
  "message": "success",
  "data": {
    "total": 100,
    "records": [
      {
        "id": 1,
        "device_id": "BF-001",
        "bird_name": "麻雀",
        "confidence": 0.96,
        "image_url": "/uploads/low_confidence/20260514/demo.jpg",
        "battery": 85,
        "food_level": 72,
        "location": "后山林区",
        "created_at": "2026-05-14 10:30:00"
      }
    ],
    "summary": {
      "total_count": 100,
      "species_count": 12,
      "today_count": 8,
      "avg_confidence": 0.91
    }
  }
}
```

### 8.5 GET `/api/bird/history/export`

用途：按筛选条件导出 CSV。

响应：

- Content-Type: `text/csv;charset=utf-8`
- 文件需包含 BOM，方便 Windows Excel 打开。
- CSV 列：ID、设备ID、鸟类名称、置信度、电池、饲料余量、位置、时间。

### 8.6 GET `/api/device/config/{device_id}`

响应：

```json
{
  "ok": true,
  "message": "success",
  "data": {
    "device_id": "BF-001",
    "capture_interval": 300,
    "confidence_threshold": 0.85,
    "upload_image": true,
    "night_mode": true,
    "low_battery_threshold": 20
  }
}
```

### 8.7 POST `/api/device/config/{device_id}`

请求体：

```json
{
  "capture_interval": 300,
  "confidence_threshold": 0.85,
  "upload_image": true,
  "night_mode": true,
  "low_battery_threshold": 20
}
```

响应：返回更新后的配置。

### 8.8 POST `/api/device/command`

用途：向设备下发命令，供后续边缘设备轮询或 MQTT 下发扩展。

请求体：

```json
{
  "device_id": "BF-001",
  "command": "take_photo"
}
```

支持命令：

- `take_photo`
- `restart`
- `update_config`

响应：

```json
{
  "ok": true,
  "message": "命令已下发",
  "data": {
    "id": 1,
    "device_id": "BF-001",
    "command": "take_photo",
    "status": "pending",
    "created_at": "2026-05-14 10:30:00"
  }
}
```

### 8.9 GET `/api/device/logs`

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| device_id | string | 可选 |
| type | string | INFO/WARNING/ERROR |

响应：

```json
{
  "ok": true,
  "message": "success",
  "data": {
    "logs": [
      {
        "id": 1,
        "device_id": "BF-001",
        "type": "INFO",
        "message": "设备上线",
        "created_at": "2026-05-14 10:30:00"
      }
    ]
  }
}
```

## 9. 边缘设备 HTTP 上传接口

### POST `/upload`

用途：边缘设备上传低置信度图片。

认证：表单字段 `api_key` + `device_id`。

Content-Type：`multipart/form-data`

表单字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| image | file | 是 | 图片文件 |
| x1 | float | 是 | 检测框 x1 |
| y1 | float | 是 | 检测框 y1 |
| x2 | float | 是 | 检测框 x2 |
| y2 | float | 是 | 检测框 y2 |
| confidence | float | 是 | 置信度 |
| class_id | int | 是 | 类别 ID |
| timestamp | float | 是 | Unix 秒时间戳 |
| rule_triggered | string | 否 | 触发规则 |
| device_id | string | 是 | 设备 ID |
| api_key | string | 是 | 设备 API Key |

处理流程：

1. 校验 `device_id` 和 `api_key` 是否匹配启用状态的 `Device`。
2. 校验图片大小不超过 `MAX_UPLOAD_SIZE_MB`。
3. 校验扩展名和 MIME，允许 `jpg`、`jpeg`、`png`。
4. 将 `timestamp` 转为 `datetime`。
5. 查询 `SpeciesDict.class_id`，不存在时允许 `species_id = null`，但需记录日志。
6. 保存图片到：

```txt
UPLOAD_BASE_DIR/{YYYYMMDD}/{device_id}_{timestamp}_{uuid}.{ext}
```

7. 写入 `LowConfidenceImage`，`review_status = pending`。
8. 返回上传结果。

响应：

```json
{
  "status": "ok",
  "path": "/uploads/low_confidence/20250331/birdcam_layer8_1743389554_abcd.jpg"
}
```

失败示例：

```json
{
  "status": "error",
  "message": "invalid device api key"
}
```

## 10. MQTT 消费逻辑

### 10.1 启动方式

FastAPI 启动时在 lifespan 中创建 MQTT 后台任务：

```python
asyncio.create_task(mqtt_consumer())
```

关闭应用时必须取消任务并关闭 MQTT 连接。

### 10.2 连接配置

从环境变量读取：

- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_USER`
- `MQTT_PASSWORD`
- `MQTT_TLS_CA_PATH`
- `MQTT_TOPIC_EVENT`
- `MQTT_TOPIC_STATUS`

MQTT Broker 已在外部配置 TLS、用户名和密码。后端只负责使用配置连接。

### 10.3 订阅主题

| 主题 | 用途 |
| --- | --- |
| `birdcam/event` | 识别事件 |
| `birdcam/status` | 设备状态 |

### 10.4 `birdcam/event` 消息格式

示例：

```json
{
  "event_type": "leave",
  "device_id": "birdcam_layer8",
  "track_id": 123,
  "timestamp": 1743389554.123,
  "confidence": 0.9321,
  "class_id": 16,
  "x1": 120.5,
  "y1": 88.2,
  "x2": 302.1,
  "y2": 244.9,
  "video_path": "/videos/20250331/demo.mp4"
}
```

处理规则：

- `event_type == "leave"`：写入 `EventLeave`。
- `event_type == "enter"`：忽略，不入库。
- `device_id` 不存在：
  - 开发环境允许自动创建设备，`name = device_id`，`api_key` 生成随机值并记录日志。
  - 生产环境建议拒绝或告警，具体由 `AUTO_CREATE_DEVICE_FROM_MQTT` 配置控制。
- `class_id` 不存在：`species = null`，`species_name = null`，保留 `raw_payload`。

### 10.5 `birdcam/status` 消息格式

示例：

```json
{
  "device_id": "birdcam_layer8",
  "timestamp": 1743389554.123,
  "cpu_temperature": 48.5,
  "memory_usage": {
    "total_mb": 8192,
    "available_mb": 3200.5,
    "percent": 60.9
  },
  "disk_usage": {
    "total_gb": 128,
    "free_gb": 45.3,
    "percent": 64.6
  },
  "battery": 85,
  "food_level": 72,
  "network": "4G"
}
```

处理规则：

- 解析 `timestamp`。
- 查找或创建 `Device`。
- 写入 `DeviceStatus`。
- 写入一条可选 `SystemLog`，例如设备上线、低电量、磁盘空间不足。

### 10.6 断线重连

要求：

- MQTT 连接失败或断开后无限重试。
- 重试间隔使用 `MQTT_RECONNECT_INTERVAL_SECONDS`。
- 每次失败记录 ERROR 日志。
- 成功连接、订阅主题、收到消息记录 INFO 日志。
- 单条消息处理失败不能导致消费者退出。

## 11. 安全配置

### 11.1 静态 Token

- 用于前端大屏 `/api/*`。
- 请求头：`X-API-Token`。
- 只通过 HTTPS 传输。
- 不应写死在后端代码中，必须从 `.env` 读取。
- 前端可通过构建环境变量注入，但需认识到前端静态 Token 不是用户级认证，只是基础访问控制。

### 11.2 设备 API Key

- 每台设备一个唯一 API Key。
- 存储在 `Device.api_key`。
- 用于 `/upload`，表单字段为 `api_key`。
- 校验时必须同时匹配 `device_id` 和 `api_key`。
- 初始化脚本生成后必须输出明文 Key 供设备配置，后续不应在普通日志中打印完整 Key。

### 11.3 Nginx 与 HTTPS

生产部署必须满足：

- `/api/` 反向代理到 FastAPI。
- `/upload` 反向代理到 FastAPI。
- `/uploads/` 指向后端静态图片目录。
- 启用 HTTPS。
- 配置频率限制：

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://127.0.0.1:8000;
}

location /upload {
    limit_req zone=api_limit burst=10 nodelay;
    proxy_pass http://127.0.0.1:8000;
}
```

### 11.4 CORS

- 生产环境只允许前端域名。
- 开发环境可允许 `http://localhost:*`。
- 不允许生产环境长期使用 `allow_origins=["*"]` 搭配敏感 Token。

## 12. 初始化脚本要求

### 12.1 `scripts/init_db.py`

首次部署运行。

职责：

1. 读取 `.env`。
2. 初始化 Tortoise。
3. 调用 `Tortoise.generate_schemas()` 或执行 aerich 迁移。
4. 写入 `SpeciesDict` 0 到 17 的物种字典。
5. 预置 12 台设备，并为每台设备写入 `device_id`、`name`、经纬度、位置描述、启用状态。
6. 为每台预置设备生成 `api_key`。
7. 输出设备清单到控制台和 `logs/init_devices_keys.txt`。
8. 关闭数据库连接。

### 12.2 物种字典

| class_id | species_en | species_cn |
| --- | --- | --- |
| 0 | Black-winged Cuckoo Shrike | 黑翅雀鹎 |
| 1 | Dark Green White-eye | 暗绿绣眼鸟 |
| 2 | White-browed Laughingthrush | 白颊噪鹛 |
| 3 | Light-vented Bulbul | 白头鹎 |
| 4 | Silver Pheasant female | 白鹇（雌） |
| 5 | Silver Pheasant male | 白鹇（雄） |
| 6 | Scaly-breasted Munia | 斑文鸟 |
| 7 | Black-throated Bushtit | 银喉长尾山雀 |
| 8 | Red-billed Blue Magpie | 红嘴蓝鹊 |
| 9 | Yellow-bellied Tit | 黄腹山雀 |
| 10 | Yellow-browed Bunting | 黄眉鹀 |
| 11 | Grey-headed Black-faced Bunting | 灰头鹀 |
| 12 | Azure-winged Magpie | 灰喜鹊 |
| 13 | Eurasian Tree Sparrow | 树麻雀 |
| 14 | Blackbird | 乌鸫 |
| 15 | Magpie | 喜鹊 |
| 16 | Little Egret | 白鹭 |
| 17 | Vinous-throated Parrotbill | 红嘴相思鸟 |

### 12.3 预置设备

初始化脚本必须预置 12 台设备。字段包括：

- `device_id`
- `name`
- `latitude`
- `longitude`
- `location_desc`
- `api_key`
- `install_date`
- `status`

API Key 使用：

```python
secrets.token_hex(32)
```

## 13. 静态文件与上传目录

FastAPI 需要挂载静态目录：

```txt
/uploads -> app/static/uploads
```

低置信度图片 URL 必须形如：

```txt
/uploads/low_confidence/20250331/birdcam_layer8_1743389554_abcd.jpg
```

文件命名要求：

- 包含 `device_id`。
- 包含 Unix timestamp。
- 包含 UUID 或随机短 ID，避免重名。
- 保留原始扩展名或统一转为 `.jpg`。

## 14. 日志要求

必须记录：

- FastAPI 启动和关闭。
- Tortoise 初始化和关闭。
- MQTT 连接、订阅、重连、消息处理失败。
- `/upload` 成功和失败。
- Token 校验失败，但不能打印完整 Token。
- 设备 API Key 校验失败，但不能打印完整 API Key。
- 数据库写入异常。

日志文件建议：

```txt
logs/app.log
logs/mqtt.log
logs/upload.log
```

## 15. 开发与启动

### 15.1 Windows 开发启动

`backend/scripts/dev_run.bat`：

```bat
cd /d %~dp0..
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 15.2 生产启动

推荐 systemd：

```ini
[Unit]
Description=Birdcam FastAPI Backend
After=network.target mysql.service

[Service]
WorkingDirectory=/opt/birdcam_project/backend
ExecStart=/opt/birdcam_project/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 16. 验收标准

后端实现完成后必须满足：

- `GET /api/dashboard/statistics` 携带正确 `X-API-Token` 返回 200。
- `/api/*` 不携带 Token 返回 401。
- `/upload` 使用错误 `api_key` 返回 401。
- `/upload` 使用正确 `device_id` + `api_key` 可上传图片并写入 `LowConfidenceImage`。
- MQTT 收到 `birdcam/event` 的 `leave` 消息后写入 `EventLeave`。
- MQTT 收到 `birdcam/status` 后写入 `DeviceStatus`。
- 断开 MQTT Broker 后消费者自动重连。
- 初始化脚本能创建表、写入 18 条物种字典、预置 12 台设备并生成设备 API Key。
- 前端大屏所有接口返回字段与本文档一致。
- 当前 Vue 管理端兼容接口不再触发 Mock fallback。

## 17. 非目标

当前版本不要求实现：

- 用户登录和 RBAC 权限。
- 多租户。
- 云对象存储。
- WebSocket 实时推送。
- 复杂模型训练或推理逻辑。

这些功能可在后续版本扩展。
