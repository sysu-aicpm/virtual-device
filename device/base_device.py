import threading
import time
import requests
from abc import ABC, abstractmethod
from datetime import datetime

class BaseDevice(ABC):
    def __init__(self, device_id, device_type):
        self.device_id = device_id
        self.device_type = device_type
        self.power = 0  # 功耗
        self.status = "off"  # 设备状态
        self.last_update = datetime.now().isoformat()
        self._stop_heartbeat = False
        self._heartbeat_thread = None

    def start_heartbeat(self, controller_url, interval=5):
        """启动心跳线程"""
        def _heartbeat():
            while not self._stop_heartbeat:
                try:
                    self._send_heartbeat(controller_url)
                    time.sleep(interval)
                except Exception as e:
                    print(f"心跳发送失败: {e}")
                    time.sleep(1)

        self._heartbeat_thread = threading.Thread(target=_heartbeat)
        self._heartbeat_thread.daemon = True
        self._heartbeat_thread.start()

    def stop_heartbeat(self):
        """停止心跳线程"""
        self._stop_heartbeat = True
        if self._heartbeat_thread:
            self._heartbeat_thread.join()

    def _send_heartbeat(self, controller_url):
        """发送心跳数据"""
        data = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "status": self.status,
            "timestamp": datetime.now().isoformat()
        }
        requests.post(f"{controller_url}/heartbeat", json=data)

    def get_info(self, keys):
        """获取设备信息"""
        info = {}
        for key in keys:
            if hasattr(self, key):
                info[key] = getattr(self, key)
        return info

    @abstractmethod
    def control(self, action, params):
        """控制设备（需要子类实现）"""
        pass

    def send_event(self, controller_url, event_type, event_data):
        """发送事件到控制器"""
        data = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        try:
            response = requests.post(f"{controller_url}/event", json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"事件发送失败: {e}")
            return False 