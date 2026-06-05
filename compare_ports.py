import json
from datetime import datetime

from alerts import create_port_alert

def run_compare_ports():

    try:
        with open(
            "data/scan_history.json",
            "r"
        ) as file:
            current_scans = json.load(file)
    except:
        current_scans = []

    try:
        with open(
            "data/previous_scan.json",
            "r"
        ) as file:
            previous_scans = json.load(file)
    except:
        previous_scans = []

    new_port_count = 0

    for current in current_scans:

        ip = current["ip"]

        current_ports = set(
            current["open_ports"]
        )

        old_ports = set()

        for previous in previous_scans:

            if previous["ip"] == ip:

                old_ports = set(
                    previous["open_ports"]
                )

                break

        new_ports = current_ports - old_ports

        for port in new_ports:

            create_port_alert(ip, port)
            new_port_count += 1

    with open(
        "data/previous_scan.json",
        "w"
    ) as file:

        json.dump(
            current_scans,
            file,
            indent=4
        )

    print(
        f"Port comparison complete — {new_port_count} new ports found"
    )

    return new_port_count

if __name__ == "__main__":
    run_compare_ports()