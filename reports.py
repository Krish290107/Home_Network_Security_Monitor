import csv
import html
from datetime import datetime
import storage
from risk_score import calculate_risk_score, risk_label
from vendor import lookup_vendor
SEVERITY_COLORS = {'CRITICAL': '#e83030', 'HIGH': '#ff6b35', 'MEDIUM': '#ffa500', 'LOW': '#3498db', 'INFO': '#2ecc71', 'MINIMAL': '#2ecc71'}
CSV_FIELDS = ['IP', 'MAC', 'Vendor', 'Open Ports', 'Alert Count']

def _esc(value):
    return html.escape(str(value), quote=True)

def _alert_counts_by_ip(alerts):
    counts = {}
    for alert in alerts:
        ip = alert.get('ip')
        if ip and ip != 'N/A':
            counts[ip] = counts.get(ip, 0) + 1
    return counts

def build_rows():
    devices = storage.load_list(storage.DEVICES_FILE)
    scans = storage.load_list(storage.SCAN_HISTORY_FILE)
    alerts = storage.load_list(storage.ALERTS_FILE)
    ports_by_ip = {scan.get('ip'): scan.get('open_ports', []) for scan in scans if scan.get('ip')}
    alert_counts = _alert_counts_by_ip(alerts)
    rows = []
    for device in devices:
        ip = device.get('ip', '')
        mac = device.get('mac', '')
        rows.append({'IP': ip, 'MAC': mac, 'Vendor': device.get('vendor') or lookup_vendor(mac), 'Open Ports': ','.join((str(p) for p in ports_by_ip.get(ip, []))), 'Alert Count': alert_counts.get(ip, 0)})
    return (rows, alerts)

def _write_csv(rows):
    with open(storage.CSV_REPORT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def _device_rows_html(rows):
    if not rows:
        return '<tr><td colspan="5" style="color:#484f5e;text-align:center">No devices discovered yet</td></tr>'
    chunks = []
    for row in rows:
        chunks.append(f'\n        <tr>\n          <td>{_esc(row['IP'])}</td>\n          <td style="font-size:12px;color:#adb3c0">{_esc(row['MAC'])}</td>\n          <td style="color:#e83030">{_esc(row['Vendor'])}</td>\n          <td>{_esc(row['Open Ports']) or '-'}</td>\n          <td>{_esc(row['Alert Count'])}</td>\n        </tr>')
    return ''.join(chunks)

def _alert_rows_html(alerts):
    recent = sorted(alerts, key=lambda a: a.get('time', ''), reverse=True)[:20]
    if not recent:
        return '<tr><td colspan="3" style="color:#484f5e;text-align:center">No alerts recorded</td></tr>'
    chunks = []
    for alert in recent:
        severity = str(alert.get('severity', 'INFO')).upper()
        color = SEVERITY_COLORS.get(severity, '#adb3c0')
        chunks.append(f'\n        <tr>\n          <td><span style="color:{color};font-weight:700">{_esc(severity)}</span></td>\n          <td>{_esc(alert.get('message', ''))}</td>\n          <td style="color:#484f5e;font-size:12px">{_esc(alert.get('time', ''))}</td>\n        </tr>')
    return ''.join(chunks)

def generate_report():
    with storage.LOCK:
        rows, alerts = build_rows()
        risk = calculate_risk_score()
    label = risk_label(risk['score'])
    score_color = SEVERITY_COLORS.get(label, '#adb3c0')
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _write_csv(rows)
    html_content = f"""<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Network Security Report - {_esc(generated_at)}</title>\n<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">\n<style>\n  :root{{--red:#e83030;--bg:#040608;--surface:#080a0f;--surface2:#0c0e15;\n         --border:#181b24;--text:#adb3c0;--dim:#484f5e;--white:#e8eaf0;}}\n  *{{margin:0;padding:0;box-sizing:border-box;}}\n  body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;padding:40px 48px;}}\n  h1{{font-size:22px;font-weight:800;color:var(--white);letter-spacing:1px;margin-bottom:4px;}}\n  .meta{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--dim);letter-spacing:2px;margin-bottom:32px;}}\n  .risk-box{{display:inline-flex;align-items:center;gap:20px;background:var(--surface);\n             border:1px solid {score_color};border-radius:4px;padding:20px 32px;margin-bottom:36px;}}\n  .risk-score{{font-size:48px;font-weight:800;color:{score_color};\n               text-shadow:0 0 16px {score_color}44;line-height:1;}}\n  .risk-label{{font-family:'JetBrains Mono',monospace;font-size:13px;color:{score_color};\n               letter-spacing:2px;margin-top:4px;}}\n  .risk-detail{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--dim);line-height:1.8;}}\n  h2{{font-size:14px;font-weight:700;color:var(--red);text-transform:uppercase;\n      letter-spacing:3px;margin-bottom:10px;padding-bottom:6px;\n      border-bottom:1px solid rgba(232,48,48,0.15);}}\n  .section{{margin-bottom:36px;}}\n  .table-wrap{{overflow-x:auto;}}\n  table{{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--border);\n         border-radius:3px;overflow:hidden;margin-top:4px;}}\n  th{{font-size:12px;font-weight:600;color:rgba(232,48,48,0.8);text-transform:uppercase;\n      letter-spacing:2px;padding:12px 18px;text-align:left;background:var(--surface2);\n      border-bottom:1px solid rgba(232,48,48,0.15);}}\n  td{{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--text);\n      padding:12px 18px;border-bottom:1px solid rgba(255,255,255,0.025);}}\n  tr:last-child td{{border-bottom:none;}}\n  .footer{{margin-top:40px;font-family:'JetBrains Mono',monospace;font-size:10px;\n           color:var(--dim);letter-spacing:2px;border-top:1px solid var(--border);padding-top:16px;}}\n</style>\n</head>\n<body>\n<h1>HOME NETWORK SECURITY REPORT</h1>\n<div class="meta">// Generated: {_esc(generated_at)} &nbsp;&middot;&nbsp; Home Network Security Monitor</div>\n\n<div class="risk-box">\n  <div>\n    <div class="risk-score">{risk['score']}/100</div>\n    <div class="risk-label">RISK: {_esc(label)}</div>\n  </div>\n  <div class="risk-detail">\n    Port component &nbsp;: {risk['port_score']}/50 ({risk['open_port_count']} open ports)<br>\n    Alert component: {risk['alert_score']}/50 ({risk['alert_count']} active alerts)\n  </div>\n</div>\n\n<div class="section">\n  <h2>Device Inventory</h2>\n  <div class="table-wrap">\n    <table>\n      <thead><tr><th>IP Address</th><th>MAC Address</th><th>Vendor</th><th>Open Ports</th><th>Alerts</th></tr></thead>\n      <tbody>{_device_rows_html(rows)}</tbody>\n    </table>\n  </div>\n</div>\n\n<div class="section">\n  <h2>Recent Alerts (last 20)</h2>\n  <div class="table-wrap">\n    <table>\n      <thead><tr><th>Severity</th><th>Message</th><th>Timestamp</th></tr></thead>\n      <tbody>{_alert_rows_html(alerts)}</tbody>\n    </table>\n  </div>\n</div>\n\n<div class="footer">Home Network Security Monitor &nbsp;&middot;&nbsp; network_report &nbsp;&middot;&nbsp; {_esc(generated_at)}</div>\n</body>\n</html>"""
    with open(storage.HTML_REPORT_FILE, 'w', encoding='utf-8') as handle:
        handle.write(html_content)
    print(f'CSV  report : {storage.CSV_REPORT_FILE}')
    print(f'HTML report : {storage.HTML_REPORT_FILE}')
    print(f'Risk Score  : {risk['score']}/100  [{label}]')
    return risk
if __name__ == '__main__':
    generate_report()
