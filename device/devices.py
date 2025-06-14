from .base_device import BaseDevice
import random

class Refrigerator(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "refrigerator",ip_addr,ip_port)
        self.temperature = 4  # 默认温度4℃
        self.door_open = False
        self.power = 100  # 默认功耗100W
        self.power_state = "on"  # 设备电源状态

    def control(self, action, params):
        if action == "set_temperature":
            temp = params.get("temperature")
            if temp is not None and -20 <= temp <= 10:
                self.temperature = temp
                # 更新功耗 - 温度越低，功耗越大
                self.power = 100 + (4 - temp) * 5
                self.add_event("temperature_change", {"temperature": temp})
                return True
        elif action == "switch":
            state = params.get("state")
            if state in ["on", "off"]:
                self.power_state = state
                self.power = 100 if state == "on" else 0
                self.add_event("power_state_change", {"power_state": state})
                return True
        return False

class Light(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "light",ip_addr,ip_port)
        self.brightness = 0  # 亮度0-100
        self.power = 10  # 默认功耗10W
        self.power_state = "off"  # 灯默认关闭状态

    def control(self, action, params):
        if action == "set_brightness":
            brightness = params.get("brightness")
            if brightness is not None and 0 <= brightness <= 100:
                self.brightness = brightness
                self.power_state = "on" if brightness > 0 else "off"
                # 功耗随亮度变化
                self.power = brightness / 10 if brightness > 0 else 0
                self.add_event("brightness_change", {"brightness": brightness})
                return True
        elif action == "switch":
            state = params.get("state")
            if state == "on":
                self.brightness = 100
                self.power_state = "on"
                self.power = 10
                self.add_event("power_state_change", {"power_state": "on"})
            elif state == "off":
                self.brightness = 0
                self.power_state = "off"
                self.power = 0
                self.add_event("power_state_change", {"power_state": "off"})
            return True
        return False

class Lock(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "lock",ip_addr,ip_port)
        self.locked = True
        self.power = 5  # 默认功耗5W
        self.lock_state = "locked"  # 锁默认锁定状态
        self.battery = 100  # 电池电量百分比

    def control(self, action, params):
        if action == "set_lock":
            state = params.get("state")
            if state in ["lock", "unlock"]:
                self.locked = state == "lock"
                self.lock_state = "locked" if self.locked else "unlocked"
                # 锁定/解锁时消耗一点电池
                self.battery = max(0, self.battery - 0.5)
                # 更新事件
                self.add_event("lock_state_change", {"lock_state": self.lock_state})
                self.add_event("battery_level", {"battery": self.battery})
                return True
        return False

class Camera(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "camera",ip_addr,ip_port)
        self.recording = False
        self.resolution = "1080p"
        self.power = 15  # 默认功耗15W
        self.camera_state = "standby"  # 摄像头默认待机状态
        self.storage_used = 0  # 已使用存储空间(MB)
        self.storage_rate = 0  # 存储使用速率

    def control(self, action, params):
        if action == "set_recording":
            state = params.get("state")
            if state in ["start", "stop"]:
                self.recording = state == "start"
                self.camera_state = "recording" if self.recording else "standby"
                # 更新功耗
                self.power = 25 if self.recording else 15
                
                # 如果开始录制，存储空间会增加
                if self.recording:
                    # 分辨率越高，存储使用越快
                    if self.resolution == "4k":
                        self.storage_rate = 10  # MB/秒
                    elif self.resolution == "1080p":
                        self.storage_rate = 5  # MB/秒
                    else:  # 720p
                        self.storage_rate = 2  # MB/秒
                else:
                    self.storage_rate = 0
                
                self.add_event("camera_state", {"camera_state": self.camera_state})
                return True
        elif action == "set_resolution":
            resolution = params.get("resolution")
            if resolution in ["720p", "1080p", "4k"]:
                self.resolution = resolution
                # 更新功耗 - 分辨率越高，功耗越大
                if self.recording:
                    if resolution == "4k":
                        self.power = 35
                    elif resolution == "1080p":
                        self.power = 25
                    else:  # 720p
                        self.power = 20
                self.add_event("resolution_change", {"resolution": resolution})
                return True
        return False
    
    def _get_dynamic_power_consumption(self):
        """重写动态功耗计算，考虑录制状态"""
        base_power = self.power
        # 录制时功耗波动更大
        if self.recording:
            fluctuation = base_power * random.uniform(-0.15, 0.2)
        else:
            fluctuation = base_power * random.uniform(-0.05, 0.05)
        
        # 更新存储使用
        if self.recording:
            self.storage_used += self.storage_rate
            self.add_event("storage_usage", {"storage_used_mb": self.storage_used})
            
        return round(base_power + fluctuation, 2) 