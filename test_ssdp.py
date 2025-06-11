from ssdpy import SSDPClient
import time
import requests

def test_ssdp_server(search_target="ssdp:all", timeout=5, retries=2):
    client = SSDPClient()
    print(f"Sending M-SEARCH for '{search_target}'...")

    found_devices = []
    for i in range(retries):
        print(f"Attempt {i+1}/{retries}...")
        # 发送 M-SEARCH 请求，并等待响应
        devices = client.m_search(search_target, mx=timeout)
        if devices:
            found_devices.extend(devices)
            print(f"Found {len(devices)} devices in this attempt.")
        time.sleep(1) # 短暂等待，避免发送过快

    if not found_devices:
        print(f"No SSDP devices found for '{search_target}'.")
        return

    print("\n--- Discovered SSDP Devices ---")
    unique_locations = set() # 用来去重，因为多次搜索可能发现相同的设备
    for device in found_devices:
        location = device.get('location')
        # if location not in unique_locations:
        unique_locations.add(location)
        print(f"  Location: {location}")
        print(f"  Service Type (NT): {device.get('nt')}")
        print(f"  Unique Service Name (USN): {device.get('usn')}")
        print(f"  Host: {device.get('host')}")
        print(f"  NTS: {device.get('nts')}")
        
        # 读取自定义字段（小写）
        device_id = device.get('device-id')
        device_ip = device.get('device-ip')
        device_port = device.get('device-port')
        device_status = device.get('device-status')
        
        if device_id:
            print(f"  Device ID: {device_id}")
        if device_ip:
            print(f"  Device IP: {device_ip}")
        if device_port:
            print(f"  Device Port: {device_port}")
        if device_status:
            print(f"  Device Status: {device_status}")
        
        # 尝试获取设备描述XML
        if location:
            try:
                print(f"  Fetching device description from: {location}")
                response = requests.get(location, timeout=2)
                if response.status_code == 200:
                    print(f"  Successfully fetched XML. First 200 chars:\n{response.text[:200]}...")
                else:
                    print(f"  Failed to fetch XML (Status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                print(f"  Error fetching XML: {e}")
        print("-" * 30)

if __name__ == "__main__":
    # 示例1: 搜索所有设备
    test_ssdp_server("ssdp:all")

    # 示例2: 如果你的设备发布了特定的服务类型，可以更精确地搜索
    # test_ssdp_server("urn:schemas-example-com:device:refrigerator:1")