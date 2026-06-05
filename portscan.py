import os
import json
import sys

import nmap
from dotenv import load_dotenv

from alerts import create_port_alert, create_scan_alert

load_dotenv()

NMAP_PATH = os.getenv("NMAP_PATH")

if not NMAP_PATH:
    print("ERROR: NMAP_PATH not set in .env file")
    print("Please set NMAP_PATH in your .env file")
    sys.exit(1)

if not os.path.exists(NMAP_PATH):
    print(f"ERROR: Nmap not found at: {NMAP_PATH}")
    print("Please install Nmap or update NMAP_PATH in .env")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

def load_previous_scan():

    try:
        with open("data/scan_history.json", "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_previous_ports(previous_scan, ip):

    for device in previous_scan:

        if device.get("ip") == ip:
            return set(device.get("open_ports", []))

    return set()

def run_port_scan():

    scanner = nmap.PortScanner(
        nmap_search_path=(NMAP_PATH,)
    )

    try:
        with open("data/devices.json", "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print("ERROR: data/devices.json not found")
        print("Run scanner.py first to discover devices")
        return []
    except json.JSONDecodeError:
        print("ERROR: data/devices.json is corrupted")
        return []

    if not devices:
        print("No devices found in inventory")
        return []

    previous_scan = load_previous_scan()

    scan_results = []

    for device in devices:

        ip = device["ip"]

        print(f"\nScanning {ip}...")

        try:

            scanner.scan(
                ip,
                arguments="-sT -F"
            )

            open_ports = []

            if ip in scanner.all_hosts():

                for protocol in scanner[ip].all_protocols():

                    ports = scanner[ip][protocol].keys()

                    for port in sorted(ports):

                        if scanner[ip][protocol][port]["state"] == "open":
                            open_ports.append(port)

            result = {
                "ip": ip,
                "open_ports": open_ports
            }

            scan_results.append(result)

            previous_ports = get_previous_ports(
                previous_scan, ip
            )
            current_ports = set(open_ports)
            new_ports = current_ports - previous_ports

            for port in new_ports:
                create_port_alert(ip, port)

            print(f"Open Ports: {open_ports}")

            if new_ports:
                print(
                    f"⚠ NEW PORTS: {sorted(new_ports)}"
                )

        except Exception as error:

            print(f"Scan failed for {ip}: {error}")

    with open(
        "data/scan_history.json",
        "w"
    ) as file:

        json.dump(
            scan_results,
            file,
            indent=4
        )

    create_scan_alert(
        "Port scan",
        len(devices)
    )

    print("\nScan History Updated")

    return scan_results

if __name__ == "__main__":
    run_port_scan()