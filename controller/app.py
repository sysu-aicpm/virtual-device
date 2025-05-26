from flask import Flask, request, jsonify
from datetime import datetime
import json
from tabulate import tabulate
import threading
import os

app = Flask(__name__)

# 存储设备信息
devices = {}
# 存储设备事件历史
event_history = []
# 最大事件历史记录数
MAX_EVENT_HISTORY = 100

def get_device_info(device_id):
    """获取设备信息的格式化字符串"""
    device = devices.get(device_id, {})
    if not device:
        return None
    
    info = [
        ["属性", "值"],
        ["设备ID", device.get("device_id", "")],
        ["设备类型", device.get("device_type", "")],
        ["状态", device.get("status", "")],
        ["最后更新", device.get("last_update", "")]
    ]
    return tabulate(info, headers="firstrow", tablefmt="grid")

def print_event(event_data):
    """打印事件信息"""
    print("\n=== 新事件通知 ===")
    event_info = [
        ["字段", "值"],
        ["设备ID", event_data.get("device_id", "")],
        ["设备类型", event_data.get("device_type", "")],
        ["事件类型", event_data.get("event_type", "")],
        ["事件数据", json.dumps(event_data.get("event_data", {}), ensure_ascii=False)],
        ["时间戳", event_data.get("timestamp", "")]
    ]
    print(tabulate(event_info, headers="firstrow", tablefmt="grid"))

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """接收设备心跳"""
    data = request.json
    device_id = data.get('device_id')
    if device_id:
        data['last_update'] = datetime.now().isoformat()
        devices[device_id] = data
        print(f"\n=== 心跳包 ===\n{get_device_info(device_id)}")
    return jsonify({"status": "ok"})

@app.route('/event', methods=['POST'])
def event():
    """接收设备事件"""
    event_data = request.json
    # 添加到历史记录
    event_history.append(event_data)
    if len(event_history) > MAX_EVENT_HISTORY:
        event_history.pop(0)
    # 打印事件信息
    print_event(event_data)
    return jsonify({"status": "ok"})

@app.route('/devices', methods=['GET'])
def list_devices():
    """列出所有设备"""
    result = []
    for device_id, device in devices.items():
        result.append({
            "device_id": device_id,
            "device_type": device.get("device_type"),
            "status": device.get("status"),
            "last_update": device.get("last_update")
        })
    return jsonify(result)

@app.route('/events', methods=['GET'])
def list_events():
    """获取事件历史"""
    return jsonify(event_history)

@app.route('/device/<device_id>', methods=['GET'])
def get_device(device_id):
    """获取特定设备信息"""
    device = devices.get(device_id)
    if device:
        return jsonify(device)
    return jsonify({"error": "设备不存在"}), 404

def clear_inactive_devices():
    """清理不活跃的设备（超过30秒没有心跳）"""
    while True:
        current_time = datetime.now()
        inactive_devices = []
        for device_id, device in devices.items():
            last_update = datetime.fromisoformat(device['last_update'])
            if (current_time - last_update).seconds > 30:
                inactive_devices.append(device_id)
        
        for device_id in inactive_devices:
            print(f"\n设备离线：{device_id}")
            devices.pop(device_id, None)
        
        threading.Event().wait(10)  # 每10秒检查一次

if __name__ == '__main__':
    # 启动清理线程
    cleanup_thread = threading.Thread(target=clear_inactive_devices)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    # 启动服务器
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 