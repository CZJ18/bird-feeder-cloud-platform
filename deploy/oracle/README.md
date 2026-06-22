# Oracle Cloud Ubuntu 部署说明

目标架构：

```text
边缘设备
-> 老师 MQTT Broker
-> Oracle 后端 MQTT Worker
-> Oracle MySQL
-> Oracle FastAPI
-> Vercel 前端
```

## 1. 服务器目录

建议把后端放到：

```bash
/opt/birdcam/backend
```

建议把 MQTT 证书放到：

```bash
/opt/birdcam/backend/certs/mqtt_ca.crt
```

图片先存本地：

```bash
/opt/birdcam/backend/uploads/low_confidence
```

## 2. MySQL

在 Oracle Ubuntu 服务器安装 MySQL 后创建数据库和用户：

```bash
mysql -u root -p
CREATE DATABASE birdcam_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'birdcam_user'@'localhost' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON birdcam_db.* TO 'birdcam_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. 后端环境变量

复制：

```bash
cp .env.example .env
```

重点修改：

```bash
DB_PASSWORD=你的 MySQL 密码
DASHBOARD_API_TOKEN=前端访问 API 用的静态 Token
MQTT_HOST=老师提供的 Broker 地址
MQTT_PORT=老师提供的端口
MQTT_USER=老师提供的用户名
MQTT_PASSWORD=老师提供的密码
MQTT_TLS_CA_PATH=/opt/birdcam/backend/certs/mqtt_ca.crt
CORS_ORIGINS=https://你的 Vercel 域名
```

生产建议：

```bash
ENABLE_MQTT=false
```

FastAPI 不直接跑 MQTT，MQTT 由独立 worker 服务运行。

## 4. Python 环境

```bash
cd /opt/birdcam/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

初始化数据库：

```bash
python scripts/init_db.py
python scripts/seed_species.py
python scripts/seed_devices.py
```

## 5. systemd 服务

复制服务文件：

```bash
sudo cp /opt/birdcam/deploy/oracle/birdcam-api.service /etc/systemd/system/
sudo cp /opt/birdcam/deploy/oracle/birdcam-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable birdcam-api birdcam-worker
sudo systemctl start birdcam-api birdcam-worker
```

查看状态：

```bash
sudo systemctl status birdcam-api
sudo systemctl status birdcam-worker
```

查看日志：

```bash
journalctl -u birdcam-api -f
journalctl -u birdcam-worker -f
```

## 6. Nginx

复制 Nginx 配置：

```bash
sudo cp /opt/birdcam/deploy/oracle/nginx-birdcam.conf /etc/nginx/sites-available/birdcam
sudo ln -s /etc/nginx/sites-available/birdcam /etc/nginx/sites-enabled/birdcam
sudo nginx -t
sudo systemctl reload nginx
```

如果先不用域名，可以把 `server_name` 改成 Oracle 公网 IP。

## 7. Vercel 前端环境变量

在 Vercel 项目环境变量里设置：

```bash
VITE_API_BASE_URL=http://你的 Oracle 公网 IP/api
VITE_DASHBOARD_API_TOKEN=和后端 DASHBOARD_API_TOKEN 一样的值
```

如果后续配了 HTTPS 域名：

```bash
VITE_API_BASE_URL=https://你的后端域名/api
```

修改 Vercel 环境变量后，需要重新部署前端。

## 8. 对外端口

Oracle 安全列表和 Ubuntu 防火墙至少需要放行：

```text
80/tcp    Nginx HTTP
443/tcp   Nginx HTTPS，可后续配置
```

如果不走 Nginx，直接暴露 FastAPI，则临时放行：

```text
8000/tcp
```

生产更建议只暴露 80/443，由 Nginx 反代到本机 8000。
