import json
import os
from datetime import datetime
from alerts import create_alert

os.makedirs("data", exist_ok=True)

def load_devices():

    try:
        with open("data/devices.json", "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_devices(devices):

    with open("data/devices.json", "w") as file:
        json.dump(devices, file, indent=4)

def update_inventory(current_devices):

    inventory = load_devices()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    for device in current_devices:

        found = False

        for existing in inventory:

            if existing["mac"] == device["mac"]:

                existing["last_seen"] = current_time

                found = True
                break

        if not found:

            device["first_seen"] = current_time
            device["last_seen"] = current_time

            inventory.append(device)

            create_alert(
                device["ip"],
                device["mac"]
            )

    save_devices(inventory)

    return inventory