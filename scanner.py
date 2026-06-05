from scapy.all import ARP, Ether, srp
from database import update_inventory
from alerts import create_scan_alert
import socket
import os

os.makedirs("data", exist_ok=True)

def get_local_ip():
    
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return socket.gethostbyname(
            socket.gethostname()
        )

def run_network_scan():

    local_ip = get_local_ip()

    target_ip = ".".join(
        local_ip.split(".")[:3]
    ) + ".0/24"

    print(
        f"Detected Network: {target_ip}"
    )

    arp = ARP(
        pdst=target_ip
    )

    ether = Ether(
        dst="ff:ff:ff:ff:ff:ff"
    )

    packet = ether / arp

    result = srp(
        packet,
        timeout=3,
        verbose=0
    )[0]

    devices = []

    print("\nDevices Found:\n")

    for sent, received in result:

        device = {
            "ip": received.psrc,
            "mac": received.hwsrc
        }

        devices.append(device)

        print(
            f"IP: {received.psrc}    MAC: {received.hwsrc}"
        )

    inventory = update_inventory(
        devices
    )

    create_scan_alert(
        "Network scan",
        len(devices)
    )

    print(
        "\nInventory Updated"
    )

    return inventory

if __name__ == "__main__":
    run_network_scan()