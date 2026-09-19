import ipaddress
import os
import socket
from dotenv import load_dotenv
from scapy.all import ARP, Ether, srp
import storage
from alerts import create_scan_alert
from database import update_inventory
load_dotenv()

def get_local_ip():
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return '127.0.0.1'
    finally:
        if sock is not None:
            sock.close()

def get_target_range():
    configured = (os.getenv('NETWORK_RANGE') or '').strip()
    if configured:
        try:
            return str(ipaddress.ip_network(configured, strict=False))
        except ValueError:
            print(f"WARNING: NETWORK_RANGE '{configured}' is not a valid network. Falling back to auto-detection.")
    local_ip = get_local_ip()
    try:
        return str(ipaddress.ip_network(f'{local_ip}/24', strict=False))
    except ValueError:
        return '192.168.1.0/24'

def run_network_scan():
    target_range = get_target_range()
    print(f'Detected Network: {target_range}')
    packet = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=target_range)
    try:
        answered = srp(packet, timeout=3, verbose=0)[0]
    except PermissionError:
        print('ERROR: raw packet capture needs elevated privileges.')
        print('Run with sudo (Linux/macOS) or as Administrator (Windows).')
        return []
    except OSError as error:
        print(f'ERROR: network scan failed: {error}')
        print('On Windows, check that Npcap is installed.')
        return []
    devices = []
    print('\nDevices Found:\n')
    for _sent, received in answered:
        mac = storage.normalize_mac(received.hwsrc)
        devices.append({'ip': received.psrc, 'mac': mac})
        print(f'IP: {received.psrc:<16} MAC: {mac}')
    if not devices:
        print('(none)')
    inventory = update_inventory(devices)
    create_scan_alert('Network scan', len(devices))
    print('\nInventory Updated')
    return inventory
if __name__ == '__main__':
    run_network_scan()
