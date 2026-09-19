import os
import threading
from datetime import datetime
from dotenv import load_dotenv
from history import run_update_history
from portscan import run_port_scan
from scanner import run_network_scan
from stats import record_snapshot
load_dotenv()

def _interval(name, default):
    raw = os.getenv(name)
    try:
        value = int(raw) if raw else default
    except ValueError:
        value = default
    return max(10, value)
NETWORK_SCAN_INTERVAL = _interval('NETWORK_SCAN_INTERVAL', 60)
PORT_SCAN_INTERVAL = _interval('PORT_SCAN_INTERVAL', 300)
PORT_SCAN_START_DELAY = 30
_CYCLE_LOCK = threading.Lock()
_STOP = threading.Event()

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] {message}', flush=True)

def network_scan_loop():
    while not _STOP.is_set():
        try:
            with _CYCLE_LOCK:
                log('Starting network scan...')
                run_network_scan()
                log('Updating device history...')
                run_update_history()
                log('Recording stats snapshot...')
                record_snapshot()
            log('Network scan cycle complete.')
        except Exception as error:
            log(f'Network scan error: {error}')
        _STOP.wait(NETWORK_SCAN_INTERVAL)

def port_scan_loop():
    if _STOP.wait(PORT_SCAN_START_DELAY):
        return
    while not _STOP.is_set():
        try:
            with _CYCLE_LOCK:
                log('Starting port scan...')
                run_port_scan()
                log('Updating device history...')
                run_update_history()
                log('Recording stats snapshot...')
                record_snapshot()
            log('Port scan cycle complete.')
        except Exception as error:
            log(f'Port scan error: {error}')
        _STOP.wait(PORT_SCAN_INTERVAL)

def start_scheduler():
    log('=' * 50)
    log('SCHEDULER STARTED')
    log(f'Network scan interval: {NETWORK_SCAN_INTERVAL}s')
    log(f'Port scan interval:    {PORT_SCAN_INTERVAL}s')
    log('=' * 50)
    threads = [threading.Thread(target=network_scan_loop, daemon=True, name='NetworkScanner'), threading.Thread(target=port_scan_loop, daemon=True, name='PortScanner')]
    for thread in threads:
        thread.start()
    log('Background threads started.')
    log('Press Ctrl+C to stop.\n')
    try:
        while not _STOP.is_set():
            _STOP.wait(1)
    except KeyboardInterrupt:
        log('Scheduler stopping...')
    finally:
        _STOP.set()
    log('Scheduler stopped.')
if __name__ == '__main__':
    start_scheduler()
