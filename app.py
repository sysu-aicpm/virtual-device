from flask import Flask, request, jsonify
import threading
import uuid
import config
from device.devices import Refrigerator, Light, Lock, Camera
import random
import time
from device.base_device import BaseDevice

app = Flask(__name__)

# 创建设备实例
DEVICE_MAPPING = {
    'refrigerator': Refrigerator,
    'light': Light,
    'lock': Lock,
    'camera': Camera
}

device:BaseDevice = None

def init_device():
    global device
    device_class = DEVICE_MAPPING.get(config.DEVICE_TYPE.lower())
    if device_class:
        device = device_class(str(uuid.uuid4()),config.HOST,config.PORT)
        device.start_ssdp_service()
        device.start_heartbeat(config.CONTROLLER_URL, config.HEARTBEAT_INTERVAL)
        print(f"设备已初始化，状态: {device.status}")
    else:
        raise ValueError(f"不支持的设备类型: {config.DEVICE_TYPE}")

def generate_random_events():
    """生成随机事件"""
    while True:
        if isinstance(device, Refrigerator):
            # 随机开关冰箱门
            if random.random() < 0.3:  # 30%的概率触发
                device.door_open = not device.door_open
                device.add_event(
                    "door_state_change",
                    {"door_open": device.door_open}
                )
                
            # 随机温度变化
            if random.random() < 0.2:  # 20%的概率触发
                temp_change = random.uniform(-1, 1)
                device.temperature += temp_change
                # 限制温度范围
                device.temperature = max(-20, min(10, device.temperature))
                device.add_event("temperature_change", {"temperature": round(device.temperature, 1)})
        
        elif isinstance(device, Light):
            # 随机调节亮度
            if random.random() < 0.2:  # 20%的概率触发
                new_brightness = random.randint(0, 100)
                device.control("set_brightness", {"brightness": new_brightness})
        
        elif isinstance(device, Lock):
            # 随机锁定/解锁
            if random.random() < 0.15:  # 15%的概率触发
                current_state = device.locked
                new_state = "unlock" if current_state else "lock"
                device.control("set_lock", {"state": new_state})
            
            # 随机电池电量变化
            if random.random() < 0.1:  # 10%的概率触发
                device.battery = max(0, device.battery - random.uniform(0.1, 0.5))
                device.add_event("battery_level", {"battery": round(device.battery, 1)})
        
        elif isinstance(device, Camera):
            # 随机开始/停止录制
            if random.random() < 0.25:  # 25%的概率触发
                current_state = device.recording
                new_state = "stop" if current_state else "start"
                device.control("set_recording", {"state": new_state})
            # 随机切换分辨率
            elif random.random() < 0.1:  # 10%的概率触发
                resolutions = ["720p", "1080p", "4k"]
                new_resolution = random.choice(resolutions)
                device.control("set_resolution", {"resolution": new_resolution})

        # # 随机设备状态错误模拟
        # if random.random() < 0.05:  # 5%的概率触发
        #     if device.status == "online":
        #         device.status = "error"
        #         print(f"设备状态变为错误: {device.status}")
        #     else:
        #         device.status = "online"
        #         print(f"设备状态恢复正常: {device.status}")

        # 随机等待5-15秒
        time.sleep(random.uniform(5, 15))

@app.route('/query', methods=['POST'])
def query():
    if not request.is_json:
        return jsonify({"error": "需要JSON格式的请求"}), 400
    
    keys = request.json.get('keys', [])
    if not isinstance(keys, list):
        return jsonify({"error": "keys必须是列表"}), 400

    info = device.get_info(keys)
    return jsonify(info)

@app.route('/control', methods=['POST'])
def control():
    if not request.is_json:
        return jsonify({"error": "需要JSON格式的请求"}), 400

    action = request.json.get('action')
    params = request.json.get('params', {})

    if not action:
        return jsonify({"error": "缺少action参数"}), 400

    success = device.control(action, params)
    return jsonify({"success": success})

if __name__ == '__main__':
    init_device()
    
    # 启动随机事件生成器线程
    event_thread = threading.Thread(target=generate_random_events)
    event_thread.daemon = True
    event_thread.start()
    
    app.run(host=config.HOST, port=config.PORT) 