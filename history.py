from datetime import datetime
import storage
from vendor import lookup_vendor

def load_history():
    return storage.load_list(storage.DEVICE_HISTORY_FILE)

def save_history(history):
    storage.save_json(storage.DEVICE_HISTORY_FILE, history)

def run_update_history():
    with storage.LOCK:
        devices = storage.load_list(storage.DEVICES_FILE)
        history = load_history()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        index = {}
        for entry in history:
            mac = storage.normalize_mac(entry.get('mac'))
            if mac:
                entry['mac'] = mac
                index[mac] = entry
        for device in devices:
            mac = storage.normalize_mac(device.get('mac'))
            if not mac:
                continue
            ip = device.get('ip', '')
            vendor = lookup_vendor(mac)
            existing = index.get(mac)
            if existing is not None:
                existing['ip'] = ip
                existing['vendor'] = vendor
                existing['last_seen'] = current_time
                continue
            record = {'ip': ip, 'mac': mac, 'vendor': vendor, 'first_seen': current_time, 'last_seen': current_time}
            history.append(record)
            index[mac] = record
        save_history(history)
    print(f'Device history updated - {len(history)} devices tracked')
    return history
if __name__ == '__main__':
    run_update_history()
