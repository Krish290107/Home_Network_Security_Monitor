import os
import shutil
import sys
import nmap
from dotenv import load_dotenv
import storage
from alerts import create_scan_alert
from compare_ports import run_compare_ports
load_dotenv()

class NmapNotFound(RuntimeError):
    pass

def resolve_nmap_path():
    configured = (os.getenv('NMAP_PATH') or '').strip().strip('"')
    if configured:
        if os.path.isfile(configured):
            return configured
        raise NmapNotFound(f'Nmap not found at NMAP_PATH: {configured}\nInstall Nmap or correct NMAP_PATH in your .env file.')
    discovered = shutil.which('nmap')
    if discovered:
        return discovered
    raise NmapNotFound('NMAP_PATH is not set in .env and nmap was not found on PATH.\nInstall Nmap (https://nmap.org/download.html) and set NMAP_PATH.')

def load_previous_scan():
    return storage.load_list(storage.SCAN_HISTORY_FILE)

def get_previous_ports(previous_scan, ip):
    for device in previous_scan:
        if device.get('ip') == ip:
            return {int(port) for port in device.get('open_ports', [])}
    return set()

def run_port_scan(arguments='-sT -F'):
    try:
        nmap_path = resolve_nmap_path()
    except NmapNotFound as error:
        print(f'ERROR: {error}')
        return []
    try:
        scanner = nmap.PortScanner(nmap_search_path=(nmap_path,))
    except nmap.PortScannerError as error:
        print(f'ERROR: could not initialise Nmap: {error}')
        return []
    devices = storage.load_list(storage.DEVICES_FILE)
    if not devices:
        print('No devices in inventory. Run scanner.py first.')
        return []
    previous_scan = load_previous_scan()
    scan_results = []
    for device in devices:
        ip = device.get('ip')
        if not ip:
            continue
        print(f'\nScanning {ip} ...')
        open_ports = []
        try:
            scanner.scan(ip, arguments=arguments)
            if ip in scanner.all_hosts():
                for protocol in scanner[ip].all_protocols():
                    for port in sorted(scanner[ip][protocol].keys()):
                        if scanner[ip][protocol][port].get('state') == 'open':
                            open_ports.append(int(port))
        except (nmap.PortScannerError, KeyError, OSError) as error:
            print(f'Scan failed for {ip}: {error}')
            continue
        scan_results.append({'ip': ip, 'open_ports': sorted(set(open_ports))})
        previous_ports = get_previous_ports(previous_scan, ip)
        new_ports = sorted(set(open_ports) - previous_ports)
        print(f'Open Ports: {sorted(set(open_ports))}')
        if new_ports:
            print(f'NEW PORTS: {new_ports}')
    storage.save_json(storage.SCAN_HISTORY_FILE, scan_results)
    run_compare_ports()
    create_scan_alert('Port scan', len(scan_results))
    print('\nScan History Updated')
    return scan_results
if __name__ == '__main__':
    results = run_port_scan()
    if not results:
        sys.exit(1)
