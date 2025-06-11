import threading
import time
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from ssdpy import SSDPServer

class BaseDevice(ABC):
    def __init__(self, device_id, device_type, ip_addr="127.0.0.1", ip_port=1900):
        self.device_id = device_id
        self.device_type = device_type
        self.power = 0  # 功耗
        self.status = "off"  # 设备状态
        self.last_update = datetime.now().isoformat()
        self._stop_heartbeat = False
        self._heartbeat_thread = None

        # SSDP 相关属性
        self.ip_addr = ip_addr
        self.ip_port = ip_port
        self._ssdp_server = None
        self._ssdp_thread = None
        self._stop_ssdp = False

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

    def start_ssdp_service(self, notify_interval=30):
        """启动 SSDP 广播服务"""
        if not self.ip_addr:
            print("SSDP IP 地址未设置，无法启动 SSDP 服务")
            return
            
        # 直接使用服务端点作为 location
        location_url = f"http://{self.ip_addr}:{self.ip_port}"
        
        # 设备类型
        device_type = f"urn:schemas-example-com:device:{self.device_type}:1"
        
        # 创建 SSDP 服务器
        self._ssdp_server = SSDPServer(
            usn=f"uuid:{self.device_id}::{device_type}",
            device_type=device_type,
            location=location_url,
            extra_fields={
                "DEVICE-ID": self.device_id,
                "DEVICE-IP": self.ip_addr,
                "DEVICE-PORT": str(self.ip_port),
                "DEVICE-STATUS": self.status
            }
        )
        
        def _ssdp_service():
            """SSDP 服务线程"""
            print(f"设备 {self.device_id} 开始 SSDP 广播，类型: {self.device_type}，地址: {location_url}")
            try:
                self._ssdp_server.serve_forever()
            except Exception as e:
                print(f"SSDP 服务异常: {e}")
        
        # 在单独线程中启动 SSDP 服务
        self._ssdp_thread = threading.Thread(target=_ssdp_service)
        self._ssdp_thread.daemon = True
        self._ssdp_thread.start()

        def stop_ssdp_service(self):
            """停止 SSDP 广播服务"""
            if self._ssdp_server:
                self._ssdp_server.stopped = True
                self._ssdp_server.sock.close()
            if self._ssdp_thread:
                self._ssdp_thread.join(timeout=1)
            print(f"设备 {self.device_id} 停止 SSDP 广播")

    def _send_heartbeat(self, controller_url):
        """发送心跳数据"""
        data = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "status": self.status,
            "timestamp": datetime.now().isoformat()
        }
        requests.post(f"{controller_url}/devices/heartbeat", json=data)

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
    
    def shutdown(self):
        """关闭设备，停止所有服务"""
        self.stop_heartbeat()
        self.stop_ssdp_service()
        print(f"设备 {self.device_id} 已关闭")