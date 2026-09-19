import json
import os
import tempfile
import threading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
DEVICES_FILE = os.path.join(DATA_DIR, 'devices.json')
ALERTS_FILE = os.path.join(DATA_DIR, 'alerts.json')
SCAN_HISTORY_FILE = os.path.join(DATA_DIR, 'scan_history.json')
PREVIOUS_SCAN_FILE = os.path.join(DATA_DIR, 'previous_scan.json')
DEVICE_HISTORY_FILE = os.path.join(DATA_DIR, 'device_history.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats_history.json')
CSV_REPORT_FILE = os.path.join(REPORTS_DIR, 'network_report.csv')
HTML_REPORT_FILE = os.path.join(REPORTS_DIR, 'network_report.html')
LOCK = threading.RLock()

def load_list(path):
    with LOCK:
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
            return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]

def save_json(path, payload):
    with LOCK:
        directory = os.path.dirname(path) or '.'
        os.makedirs(directory, exist_ok=True)
        handle_fd, temp_path = tempfile.mkstemp(dir=directory, prefix='.tmp-', suffix='.json')
        try:
            with os.fdopen(handle_fd, 'w', encoding='utf-8') as handle:
                json.dump(payload, handle, indent=4)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        except BaseException:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

def normalize_mac(mac_address):
    if not mac_address:
        return ''
    cleaned = ''.join((char for char in str(mac_address).lower() if char in '0123456789abcdef'))
    if len(cleaned) != 12:
        return str(mac_address).strip().lower()
    return ':'.join((cleaned[index:index + 2] for index in range(0, 12, 2)))
