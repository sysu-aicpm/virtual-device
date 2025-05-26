# 简单设备控制器

这是一个用于测试虚拟智能家居设备的简单控制器。它可以接收设备的心跳包和事件通知，并提供简单的查询接口。

## 功能特性

1. 接收并显示设备心跳包
2. 接收并显示设备事件通知
3. 提供设备查询接口
4. 自动清理不活跃设备
5. 保存最近100条事件历史

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python app.py
```

默认监听端口为8000，可以通过环境变量PORT修改：

```bash
PORT=8080 python app.py
```

## API接口

### 1. 列出所有设备
- 路径：`/devices`
- 方法：GET
- 响应示例：
```json
[
    {
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "device_type": "refrigerator",
        "status": "on",
        "last_update": "2024-03-20T10:30:00.000Z"
    }
]
```

### 2. 获取特定设备信息
- 路径：`/device/<device_id>`
- 方法：GET
- 响应示例：
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "refrigerator",
    "status": "on",
    "last_update": "2024-03-20T10:30:00.000Z"
}
```

### 3. 获取事件历史
- 路径：`/events`
- 方法：GET
- 响应示例：
```json
[
    {
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "device_type": "refrigerator",
        "event_type": "door_state_change",
        "event_data": {
            "door_open": true
        },
        "timestamp": "2024-03-20T10:30:00.000Z"
    }
]
```

## 测试命令

1. 查询所有设备：
```bash
curl http://localhost:8000/devices
```

2. 查询特定设备：
```bash
curl http://localhost:8000/device/550e8400-e29b-41d4-a716-446655440000
```

3. 查询事件历史：
```bash
curl http://localhost:8000/events
``` 