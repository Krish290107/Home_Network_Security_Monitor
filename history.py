import json
import os
from datetime import datetime

from vendor import lookup_vendor

os.makedirs("data", exist_ok=True)

HISTORY_FILE = "data/device_history.json"

def load_history():

    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def run_update_history():

    try:
        with open(
            "data/devices.json", "r"
        ) as file:
            devices = json.load(file)
    except:
        devices = []

    history = load_history()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    for device in devices:

        ip = device["ip"]
        mac = device["mac"]
        vendor = lookup_vendor(mac)

        found = False

        for entry in history:

            if entry["mac"] == mac:

                entry["ip"] = ip
                entry["vendor"] = vendor
                entry["last_seen"] = current_time
                found = True
                break

        if not found:

            history.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
                "first_seen": current_time,
                "last_seen": current_time
            })

    save_history(history)

    print(
        f"Device history updated — {len(history)} devices tracked"
    )

    return history

if __name__ == "__main__":
    run_update_history()