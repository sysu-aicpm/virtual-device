import os
from dotenv import load_dotenv

load_dotenv()

# 服务器配置
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
# CONTROLLER_URL = os.getenv('CONTROLLER_URL', 'http://localhost:8000')

# 心跳包配置
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 5))  # 秒

# 设备类型配置
DEVICE_TYPE = os.getenv('DEVICE_TYPE', 'refrigerator')  # base, refrigerator, light, lock, camera 