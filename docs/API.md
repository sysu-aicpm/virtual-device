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
    "status": "on",
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

### 1. 心跳包

**请求**
- URL：`{CONTROLLER_URL}/heartbeat`
- 方法：POST
- Content-Type: application/json
- 请求体：
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "refrigerator",
    "status": "on",
    "timestamp": "2024-03-20T10:30:00.000Z"
}
```

### 2. 事件通知

**请求**
- URL：`{CONTROLLER_URL}/event`
- 方法：POST
- Content-Type: application/json

**各设备支持的事件：**

#### 冰箱
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "refrigerator",
    "event_type": "door_state_change",
    "event_data": {
        "door_open": true
    },
    "timestamp": "2024-03-20T10:30:00.000Z"
}
```

#### 灯
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "light",
    "event_type": "state_change",
    "event_data": {
        "status": "on",
        "brightness": 100
    },
    "timestamp": "2024-03-20T10:30:00.000Z"
}
```

#### 门锁
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "lock",
    "event_type": "lock_state_change",
    "event_data": {
        "locked": true
    },
    "timestamp": "2024-03-20T10:30:00.000Z"
}
```

#### 摄像头
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "camera",
    "event_type": "recording_state_change",
    "event_data": {
        "recording": true,
        "resolution": "1080p"
    },
    "timestamp": "2024-03-20T10:30:00.000Z"
}
``` 