# 虚拟智能家居设备模拟器

这个项目模拟了各种智能家居设备的网络接口，支持HTTP API调用和自动事件生成。每个设备都会定期发送心跳包，并随机触发状态改变事件。

## 功能特性

1. 支持多种设备类型
   - 冰箱（温度控制、门状态监控）
   - 智能灯（亮度调节、开关控制）
   - 门锁（锁定/解锁控制）
   - 摄像头（录制控制、分辨率设置）

2. 自动行为
   - 定期发送心跳包（默认5秒）
   - 随机生成设备状态改变事件
   - 自动更新设备功耗

3. HTTP API接口
   - 设备状态查询
   - 设备控制命令
   - JSON数据格式

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量（可选）：
```bash
export HOST=0.0.0.0              # 服务器监听地址
export PORT=5000                 # 服务器端口
export CONTROLLER_URL=http://localhost:8000  # 控制器地址
export HEARTBEAT_INTERVAL=5      # 心跳间隔（秒）
export DEVICE_TYPE=refrigerator  # 设备类型
```

3. 运行设备：
```bash
python app.py
```

## 设备行为说明

### 1. 冰箱（refrigerator）

**自动行为：**
- 每5-15秒有30%概率随机开关冰箱门
- 开门时发送 door_state_change 事件
- 默认功耗100W

**API控制：**
```bash
# 设置温度（范围：-20到10℃）
curl -X POST http://localhost:5000/control \
     -H "Content-Type: application/json" \
     -d '{
           "action": "set_temperature",
           "params": {"temperature": 4}
         }'

# 查询状态
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["temperature", "door_open", "power", "status"]
         }'
```

### 2. 智能灯（light）

**自动行为：**
- 每5-15秒有20%概率随机调节亮度
- 亮度改变时自动调整功耗
- 功耗随亮度变化（0-10W）

**API控制：**
```bash
# 设置亮度（范围：0-100）
curl -X POST http://localhost:5000/control \
     -H "Content-Type: application/json" \
     -d '{
           "action": "set_brightness",
           "params": {"brightness": 80}
         }'

# 开关控制
curl -X POST http://localhost:5000/control \
     -H "Content-Type: application/json" \
     -d '{
           "action": "switch",
           "params": {"state": "on"}
         }'

# 查询状态
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["brightness", "power", "status"]
         }'
```

### 3. 门锁（lock）

**自动行为：**
- 每5-15秒有15%概率随机切换锁定状态
- 状态改变时发送 lock_state_change 事件
- 固定功耗5W

**API控制：**
```bash
# 设置锁定状态
curl -X POST http://localhost:5000/control \
     -H "Content-Type: application/json" \
     -d '{
           "action": "set_lock",
           "params": {"state": "lock"}
         }'

# 查询状态
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["locked", "status", "power"]
         }'
```

### 4. 摄像头（camera）

**自动行为：**
- 每5-15秒有25%概率随机开始/停止录制
- 每5-15秒有10%概率随机切换分辨率
- 待机功耗15W，录制时功耗25W

**API控制：**
```bash
# 控制录制
curl -X POST http://localhost:5000/control \
     -H "Content-Type: application/json" \
     -d '{
           "action": "set_recording",
           "params": {"state": "start"}
         }'

# 设置分辨率
curl -X POST http://localhost:5000/control \
     -H "Content-Type: application/json" \
     -d '{
           "action": "set_resolution",
           "params": {"resolution": "1080p"}
         }'

# 查询状态
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["recording", "resolution", "power", "status"]
         }'
```

## 事件通知

所有设备都会向控制器发送以下类型的数据：

1. 心跳包（每5秒）：
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_type": "refrigerator",
    "status": "on",
    "timestamp": "2024-03-20T10:30:00.000Z"
}
```

2. 状态改变事件：
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

## 测试建议

1. 先启动控制器：
```bash
cd controller
python app.py
```

2. 然后启动设备（可以启动多个不同类型的设备）：
```bash
# 启动冰箱
DEVICE_TYPE=refrigerator python app.py

# 启动智能灯
DEVICE_TYPE=light python app.py

# 启动门锁
DEVICE_TYPE=lock python app.py

# 启动摄像头
DEVICE_TYPE=camera python app.py
```

3. 观察控制器控制台输出，可以看到：
   - 设备心跳信息
   - 随机生成的事件
   - 设备状态变化

4. 使用curl命令或其他HTTP客户端测试API接口

## 开发扩展

如需添加新的设备类型，请参考 [开发指南](docs/开发指南.md)。
详细的API文档请参考 [API文档](docs/API.md)。
设备功能说明请参考 [设备说明](docs/设备说明.md)。
