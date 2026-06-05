import time
import threading
from datetime import datetime

from scanner import run_network_scan
from portscan import run_port_scan
from compare_ports import run_compare_ports
from history import run_update_history
from stats import record_snapshot

NETWORK_SCAN_INTERVAL = 60    
PORT_SCAN_INTERVAL = 300      

def log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(f"[{timestamp}] {message}")

def network_scan_loop():

    while True:
        try:
            log("Starting network scan...")
            run_network_scan()

            log("Updating device history...")
            run_update_history()

            log("Recording stats snapshot...")
            record_snapshot()

            log("Network scan cycle complete.")

        except Exception as error:
            log(f"Network scan error: {error}")

        time.sleep(NETWORK_SCAN_INTERVAL)

def port_scan_loop():

    while True:
        try:
            log("Starting port scan...")
            run_port_scan()

            log("Comparing port changes...")
            run_compare_ports()

            log("Updating device history...")
            run_update_history()

            log("Recording stats snapshot...")
            record_snapshot()

            log("Port scan cycle complete.")

        except Exception as error:
            log(f"Port scan error: {error}")

        time.sleep(PORT_SCAN_INTERVAL)

def start_scheduler():

    log("=" * 50)
    log("SCHEDULER STARTED")
    log(f"Network scan interval: {NETWORK_SCAN_INTERVAL}s")
    log(f"Port scan interval:    {PORT_SCAN_INTERVAL}s")
    log("=" * 50)

    network_thread = threading.Thread(
        target=network_scan_loop,
        daemon=True,
        name="NetworkScanner"
    )

    port_thread = threading.Thread(
        target=port_scan_delayed,
        daemon=True,
        name="PortScanner"
    )

    network_thread.start()
    port_thread.start()

    log("Background threads started.")
    log("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\nScheduler stopped by user.")

def port_scan_delayed():

    time.sleep(30)
    port_scan_loop()

if __name__ == "__main__":
    start_scheduler()
