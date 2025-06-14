# API 文档

## HTTP 接口

### 1. 查询设备信息

**请求**
- 路径：`/query`
- 方法：POST
- Content-Type: application/json
- 请求体：
```json
{
    "keys": ["device_id", "device_type", "power", "status", "temperature", "brightness", "locked", "recording", "resolution"]
}
```

**响应**
- Content-Type: application/json
- 状态码：200（成功）
- 响应体示例（冰箱）：
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "refrigerator",
    "power": 100,
    "status": "online",
    "temperature": 4
}
```

### 2. 控制设备

**请求**
- 路径：`/control`
- 方法：POST
- Content-Type: application/json

**响应**
- Content-Type: application/json
- 状态码：
  - 200：成功
  - 400：请求格式错误
  - 404：设备不存在
  - 500：内部错误

**各设备支持的控制命令：**

#### 冰箱
```json
{
    "action": "set_temperature",
    "params": {
        "temperature": 4  // 范围：-20到10℃
    }
}
```
或
```json
{
    "action": "switch",
    "params": {
        "state": "on"  // "on" 或 "off"
    }
}
```

#### 灯
```json
{
    "action": "set_brightness",
    "params": {
        "brightness": 80  // 范围：0-100
    }
}
```
或
```json
{
    "action": "switch",
    "params": {
        "state": "on"  // "on" 或 "off"
    }
}
```

#### 门锁
```json
{
    "action": "set_lock",
    "params": {
        "state": "lock"  // "lock" 或 "unlock"
    }
}
```

#### 摄像头
```json
{
    "action": "set_recording",
    "params": {
        "state": "start"  // "start" 或 "stop"
    }
}
```
或
```json
{
    "action": "set_resolution",
    "params": {
        "resolution": "1080p"  // "720p", "1080p" 或 "4k"
    }
}
```

## 设备主动发送的数据包

### 心跳包（包含设备事件）

**请求**
- URL：`{CONTROLLER_URL}/api/v1/devices/heartbeat/`
- 方法：POST
- Content-Type: application/json
- 请求体：
```json
{
    "device_identifier": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-03-20T10:30:00.000Z",
    "status": "online",
    "data": {
        "current_power_consumption": 102.5,
        "temperature_change": {
            "temperature": 4.2
        },
        "door_state_change": {
            "door_open": true
        }
    }
}
```

**设备状态说明**
- `online`: 设备在线正常工作
- `offline`: 设备离线
- `error`: 设备出现错误

**各设备事件数据字段**

#### 冰箱
```json
{
    "door_state_change": {
        "door_open": true
    },
    "temperature_change": {
        "temperature": 4.2
    },
    "power_state_change": {
        "power_state": "on"
    }
}
```

#### 灯
```json
{
    "brightness_change": {
        "brightness": 80
    },
    "power_state_change": {
        "power_state": "on"
    }
}
```

#### 门锁
```json
{
    "lock_state_change": {
        "lock_state": "locked"
    },
    "battery_level": {
        "battery": 95.5
    }
}
```

#### 摄像头
```json
{
    "camera_state": {
        "camera_state": "recording"
    },
    "resolution_change": {
        "resolution": "1080p"
    },
    "storage_usage": {
        "storage_used_mb": 250
    }
}
``` 