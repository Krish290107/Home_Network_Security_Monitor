from datetime import datetime
import storage
from alerts import create_alert

def load_devices():
    return storage.load_list(storage.DEVICES_FILE)

def save_devices(devices):
    storage.save_json(storage.DEVICES_FILE, devices)

def update_inventory(current_devices):
    with storage.LOCK:
        inventory = load_devices()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        index = {}
        for entry in inventory:
            mac = storage.normalize_mac(entry.get('mac'))
            if mac:
                entry['mac'] = mac
                index[mac] = entry
        for device in current_devices:
            mac = storage.normalize_mac(device.get('mac'))
            ip = device.get('ip', '')
            if not mac:
                continue
            existing = index.get(mac)
            if existing is not None:
                existing['ip'] = ip
                existing['last_seen'] = current_time
                continue
            record = {'ip': ip, 'mac': mac, 'first_seen': current_time, 'last_seen': current_time}
            inventory.append(record)
            index[mac] = record
            create_alert(ip, mac)
        save_devices(inventory)
        return inventory
