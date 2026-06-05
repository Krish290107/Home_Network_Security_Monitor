import json
import os
from datetime import datetime

os.makedirs("data", exist_ok=True)

ALERTS_FILE = "data/alerts.json"
MAX_ALERTS = 100


SEVERITY_LEVELS = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _severity_for_new_device():
    return "HIGH"


def _severity_for_port(port):
    critical_ports = {21, 22, 23, 25, 53, 135, 139, 445, 3389, 5900, 6379, 27017}
    high_ports     = {3306, 5432, 1521, 1433, 8080, 8443}
    medium_ports   = {80, 443, 8888, 9090, 9200}

    if port in critical_ports:
        return "CRITICAL"
    if port in high_ports:
        return "HIGH"
    if port in medium_ports:
        return "MEDIUM"

    if port < 1024:
        return "LOW"
    return "INFO"


def load_alerts():
    try:
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_alerts(alerts):
    alerts = alerts[-MAX_ALERTS:]
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=4)


def create_alert(ip, mac):
    alerts = load_alerts()
    severity = _severity_for_new_device()
    alert = {
        "severity": severity,
        "message": f"New device detected: {ip}",
        "ip": ip,
        "mac": mac,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    alerts.append(alert)
    save_alerts(alerts)
    print(f"⚠ ALERT [{severity}]: New device detected: {ip}")


def create_port_alert(ip, port):
    alerts = load_alerts()
    severity = _severity_for_port(port)
    alert = {
        "severity": severity,
        "message": f"New open port {port} on {ip}",
        "ip": ip,
        "port": port,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    alerts.append(alert)
    save_alerts(alerts)
    print(f"⚠ ALERT [{severity}]: New open port {port} on {ip}")


def create_scan_alert(scan_type, device_count=0):
    alerts = load_alerts()
    alert = {
        "severity": "INFO",
        "message": f"{scan_type} completed — {device_count} hosts scanned",
        "ip": "N/A",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    alerts.append(alert)
    save_alerts(alerts)
    print(f"ℹ ALERT [INFO]: {scan_type} completed")
