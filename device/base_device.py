import threading
import time
import requests
import random
from abc import ABC, abstractmethod
from datetime import datetime
from ssdpy import SSDPServer

class BaseDevice(ABC):
    def __init__(self, device_id, device_type, ip_addr="127.0.0.1", ip_port=1900):
        self.device_id = device_id
        self.device_type = device_type
        self.power = 0  # 功耗
        self.status = "offline"  # 设备状态，只支持online/offline/error
        self.last_update = datetime.now().isoformat()
        self._stop_heartbeat = False
        self._heartbeat_thread = None
        self.events = {}  # 存储设备事件

        # SSDP 相关属性
        self.ip_addr = ip_addr
        self.ip_port = ip_port
        self._ssdp_server = None
        self._ssdp_thread = None
        self._stop_ssdp = False

    def start_heartbeat(self, controller_url, interval=5):
        """启动心跳线程"""
        # 启动心跳时设备状态改为online
        self.status = "online"
        
        def _heartbeat():
            while not self._stop_heartbeat:
                try:
                    self._send_heartbeat(controller_url)
                    time.sleep(interval)
                except Exception as e:
                    print(f"心跳发送失败: {e}")
                    # 发送失败时设置状态为error
                    self.status = "error"
                    time.sleep(1)

        self._heartbeat_thread = threading.Thread(target=_heartbeat)
        self._heartbeat_thread.daemon = True
        self._heartbeat_thread.start()

    def stop_heartbeat(self):
        """停止心跳线程"""
        self._stop_heartbeat = True
        # 停止心跳时设备状态改为offline
        self.status = "offline"
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
                # SSDP服务异常时设置状态为error
                self.status = "error"
        
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
        """发送心跳数据，包含设备事件"""
        # 生成动态功耗数据
        current_power = self._get_dynamic_power_consumption()
        
        # 准备数据字段
        data_fields = {
            "current_power_consumption": current_power
        }
        
        # 合并设备特定事件
        data_fields.update(self.events)
        
        # 心跳数据
        heartbeat_data = {
            "device_identifier": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "status": self.status,  # 只使用online/offline/error三种状态
            "data": data_fields
        }
        
        print(heartbeat_data)
        requests.post(f"{controller_url}/api/v1/devices/heartbeat/", json=heartbeat_data)
        
        # 清空事件，因为已经发送
        self.events = {}

    def _get_dynamic_power_consumption(self):
        """生成动态功耗数据"""
        # 基础功耗加上随机波动 (±10%)
        base_power = self.power
        fluctuation = base_power * random.uniform(-0.1, 0.1)
        return round(base_power + fluctuation, 2)

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

    def add_event(self, event_type, event_data):
        """添加事件到事件队列，等待下次心跳发送"""
        self.events[event_type] = event_data
    
    def shutdown(self):
        """关闭设备，停止所有服务"""
        self.stop_heartbeat()
        self.stop_ssdp_service()
        print(f"设备 {self.device_id} 已关闭")