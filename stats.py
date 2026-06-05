import json
import os
from datetime import datetime

os.makedirs("data", exist_ok=True)

STATS_FILE = "data/stats_history.json"

MAX_DATAPOINTS = 50

def load_stats():

    try:
        with open(STATS_FILE, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_stats(stats):

    stats = stats[-MAX_DATAPOINTS:]

    with open(STATS_FILE, "w") as file:
        json.dump(stats, file, indent=4)

def record_snapshot():

    devices = _load_json("data/devices.json")
    alerts = _load_json("data/alerts.json")
    scans = _load_json("data/scan_history.json")

    total_ports = 0
    for device in scans:
        total_ports += len(
            device.get("open_ports", [])
        )

    snapshot = {
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),
        "devices": len(devices),
        "alerts": len(alerts),
        "open_ports": total_ports
    }

    stats = load_stats()
    stats.append(snapshot)
    save_stats(stats)

    return snapshot

def _load_json(file_path):

    try:
        with open(file_path, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []
