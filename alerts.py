from datetime import datetime
import storage
MAX_ALERTS = 200
SEVERITY_LEVELS = ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
CRITICAL_PORTS = {21, 23, 135, 139, 445, 3389, 5900, 6379, 27017}
HIGH_PORTS = {22, 25, 1433, 1521, 3306, 5432, 8080, 8443}
MEDIUM_PORTS = {53, 110, 143, 8888, 9090, 9200}
LOW_PORTS = {80, 443, 587}

def _timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _severity_for_new_device():
    return 'HIGH'

def _severity_for_port(port):
    try:
        port = int(port)
    except (TypeError, ValueError):
        return 'INFO'
    if port in CRITICAL_PORTS:
        return 'CRITICAL'
    if port in HIGH_PORTS:
        return 'HIGH'
    if port in MEDIUM_PORTS:
        return 'MEDIUM'
    if port in LOW_PORTS:
        return 'LOW'
    if port < 1024:
        return 'LOW'
    return 'INFO'

def load_alerts():
    return storage.load_list(storage.ALERTS_FILE)

def save_alerts(alerts):
    storage.save_json(storage.ALERTS_FILE, alerts[-MAX_ALERTS:])

def _append_alert(alert):
    with storage.LOCK:
        alerts = load_alerts()
        alerts.append(alert)
        save_alerts(alerts)

def create_alert(ip, mac):
    severity = _severity_for_new_device()
    _append_alert({'severity': severity, 'type': 'new_device', 'message': f'New device detected: {ip}', 'ip': ip, 'mac': mac, 'time': _timestamp()})
    print(f'ALERT [{severity}]: New device detected: {ip} ({mac})')

def create_port_alert(ip, port):
    severity = _severity_for_port(port)
    _append_alert({'severity': severity, 'type': 'new_port', 'message': f'New open port {port} on {ip}', 'ip': ip, 'port': port, 'time': _timestamp()})
    print(f'ALERT [{severity}]: New open port {port} on {ip}')

def create_scan_alert(scan_type, device_count=0):
    _append_alert({'severity': 'INFO', 'type': 'scan', 'message': f'{scan_type} completed - {device_count} hosts scanned', 'ip': 'N/A', 'time': _timestamp()})
    print(f'ALERT [INFO]: {scan_type} completed - {device_count} hosts')
