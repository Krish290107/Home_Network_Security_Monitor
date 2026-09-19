from datetime import datetime
import storage
MAX_DATAPOINTS = 50

def load_stats():
    return storage.load_list(storage.STATS_FILE)

def save_stats(stats):
    storage.save_json(storage.STATS_FILE, stats[-MAX_DATAPOINTS:])

def record_snapshot():
    with storage.LOCK:
        devices = storage.load_list(storage.DEVICES_FILE)
        alerts = storage.load_list(storage.ALERTS_FILE)
        scans = storage.load_list(storage.SCAN_HISTORY_FILE)
        total_ports = sum((len(scan.get('open_ports', [])) for scan in scans))
        snapshot = {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'devices': len(devices), 'alerts': len(alerts), 'open_ports': total_ports}
        stats = load_stats()
        stats.append(snapshot)
        save_stats(stats)
    return snapshot
if __name__ == '__main__':
    print(record_snapshot())
