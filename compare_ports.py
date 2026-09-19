import storage
from alerts import create_port_alert

def _ports_of(entry):
    ports = set()
    for port in entry.get('open_ports', []):
        try:
            ports.add(int(port))
        except (TypeError, ValueError):
            continue
    return ports

def run_compare_ports():
    with storage.LOCK:
        current_scans = storage.load_list(storage.SCAN_HISTORY_FILE)
        previous_scans = storage.load_list(storage.PREVIOUS_SCAN_FILE)
        previous_by_ip = {entry.get('ip'): _ports_of(entry) for entry in previous_scans if entry.get('ip')}
        new_port_count = 0
        for current in current_scans:
            ip = current.get('ip')
            if not ip:
                continue
            new_ports = _ports_of(current) - previous_by_ip.get(ip, set())
            for port in sorted(new_ports):
                create_port_alert(ip, port)
                new_port_count += 1
        storage.save_json(storage.PREVIOUS_SCAN_FILE, current_scans)
    print(f'Port comparison complete - {new_port_count} new ports found')
    return new_port_count
if __name__ == '__main__':
    run_compare_ports()
