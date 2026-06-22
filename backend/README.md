# 鸟类智能监测系统后端

技术栈：FastAPI + Tortoise-ORM + MySQL + aiomqtt。

## 初始化

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/init_db.py
```

## 启动

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 安全

- `/api/*` 必须携带 `X-API-Token`。
- `/upload` 使用表单字段 `device_id` + `api_key` 认证设备。
- 生产环境必须使用 HTTPS 和 Nginx 频率限制。
