from .base_device import BaseDevice

class Refrigerator(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "refrigerator",ip_addr,ip_port)
        self.temperature = 4  # 默认温度4℃
        self.door_open = False
        self.power = 100  # 默认功耗100W

    def control(self, action, params):
        if action == "set_temperature":
            temp = params.get("temperature")
            if temp is not None and -20 <= temp <= 10:
                self.temperature = temp
                return True
        return False

class Light(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "light",ip_addr,ip_port)
        self.brightness = 0  # 亮度0-100
        self.power = 10  # 默认功耗10W

    def control(self, action, params):
        if action == "set_brightness":
            brightness = params.get("brightness")
            if brightness is not None and 0 <= brightness <= 100:
                self.brightness = brightness
                self.status = "on" if brightness > 0 else "off"
                self.power = self.brightness / 10  # 功耗随亮度变化
                return True
        elif action == "switch":
            state = params.get("state")
            if state == "on":
                self.brightness = 100
                self.status = "on"
                self.power = 10
            elif state == "off":
                self.brightness = 0
                self.status = "off"
                self.power = 0
            return True
        return False

class Lock(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "lock",ip_addr,ip_port)
        self.locked = True
        self.power = 5  # 默认功耗5W

    def control(self, action, params):
        if action == "set_lock":
            state = params.get("state")
            if state in ["lock", "unlock"]:
                self.locked = state == "lock"
                self.status = "locked" if self.locked else "unlocked"
                return True
        return False

class Camera(BaseDevice):
    def __init__(self, device_id,ip_addr,ip_port):
        super().__init__(device_id, "camera",ip_addr,ip_port)
        self.recording = False
        self.resolution = "1080p"
        self.power = 15  # 默认功耗15W

    def control(self, action, params):
        if action == "set_recording":
            state = params.get("state")
            if state in ["start", "stop"]:
                self.recording = state == "start"
                self.status = "recording" if self.recording else "standby"
                self.power = 25 if self.recording else 15
                return True
        elif action == "set_resolution":
            resolution = params.get("resolution")
            if resolution in ["720p", "1080p", "4k"]:
                self.resolution = resolution
                return True
        return False 