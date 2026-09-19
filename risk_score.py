from datetime import datetime, timedelta
import storage
TOP_PORTS = {21: {'service': 'FTP', 'risk': 5}, 22: {'service': 'SSH', 'risk': 3}, 23: {'service': 'Telnet', 'risk': 5}, 25: {'service': 'SMTP', 'risk': 4}, 53: {'service': 'DNS', 'risk': 2}, 80: {'service': 'HTTP', 'risk': 2}, 135: {'service': 'MSRPC', 'risk': 4}, 139: {'service': 'NetBIOS', 'risk': 4}, 443: {'service': 'HTTPS', 'risk': 1}, 445: {'service': 'SMB', 'risk': 5}, 1433: {'service': 'MSSQL', 'risk': 4}, 1521: {'service': 'Oracle', 'risk': 4}, 3306: {'service': 'MySQL', 'risk': 4}, 3389: {'service': 'RDP', 'risk': 5}, 5432: {'service': 'PostgreSQL', 'risk': 4}, 5900: {'service': 'VNC', 'risk': 5}, 6379: {'service': 'Redis', 'risk': 4}, 8080: {'service': 'HTTP-Alt', 'risk': 3}, 8443: {'service': 'HTTPS-Alt', 'risk': 2}, 27017: {'service': 'MongoDB', 'risk': 5}}
ALERT_WEIGHTS = {'CRITICAL': 10, 'HIGH': 6, 'MEDIUM': 3, 'LOW': 1, 'INFO': 0}
PORT_SCORE_CEILING = 20
ALERT_SCORE_CEILING = 50
ALERT_WINDOW_HOURS = 24

def _alert_is_active(alert, cutoff):
    raw_time = alert.get('time')
    if not raw_time:
        return True
    try:
        return datetime.strptime(raw_time, '%Y-%m-%d %H:%M:%S') >= cutoff
    except (TypeError, ValueError):
        return True

def calculate_risk_score():
    scans = storage.load_list(storage.SCAN_HISTORY_FILE)
    alerts = storage.load_list(storage.ALERTS_FILE)
    cutoff = datetime.now() - timedelta(hours=ALERT_WINDOW_HOURS)
    active_alerts = [a for a in alerts if _alert_is_active(a, cutoff)]
    port_score_raw = 0
    open_port_count = 0
    for device in scans:
        for port in device.get('open_ports', []):
            try:
                port = int(port)
            except (TypeError, ValueError):
                continue
            open_port_count += 1
            port_score_raw += TOP_PORTS.get(port, {}).get('risk', 1)
    port_score = min(50, round(port_score_raw / PORT_SCORE_CEILING * 50))
    alert_score_raw = sum((ALERT_WEIGHTS.get(str(alert.get('severity', 'INFO')).upper(), 0) for alert in active_alerts))
    alert_score = min(50, round(alert_score_raw / ALERT_SCORE_CEILING * 50))
    return {'score': port_score + alert_score, 'port_score': port_score, 'alert_score': alert_score, 'open_port_count': open_port_count, 'alert_count': len(active_alerts)}

def risk_label(score):
    if score >= 80:
        return 'CRITICAL'
    if score >= 60:
        return 'HIGH'
    if score >= 40:
        return 'MEDIUM'
    if score >= 20:
        return 'LOW'
    return 'MINIMAL'
if __name__ == '__main__':
    result = calculate_risk_score()
    label = risk_label(result['score'])
    print(f'Risk Score : {result['score']}/100  [{label}]')
    print(f'  Port component  : {result['port_score']}/50  ({result['open_port_count']} open ports)')
    print(f'  Alert component : {result['alert_score']}/50  ({result['alert_count']} active alerts, last {ALERT_WINDOW_HOURS}h)')
