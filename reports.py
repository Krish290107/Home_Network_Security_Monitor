import json
import csv
import os
from datetime import datetime

from vendor import lookup_vendor
from risk_score import calculate_risk_score, risk_label

os.makedirs("reports", exist_ok=True)


def _load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def generate_report():
    devices = _load_json("data/devices.json")
    scans   = _load_json("data/scan_history.json")
    alerts  = _load_json("data/alerts.json")
    risk    = calculate_risk_score()
    label   = risk_label(risk["score"])
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_rows = []
    for device in devices:
        ip     = device["ip"]
        mac    = device["mac"]
        vendor = lookup_vendor(mac)

        open_ports = []
        for scan in scans:
            if scan["ip"] == ip:
                open_ports = scan["open_ports"]
                break

        alert_count = sum(
            1 for a in alerts if ip in a.get("message", "")
        )

        report_rows.append({
            "IP":          ip,
            "MAC":         mac,
            "Vendor":      vendor,
            "Open Ports":  ",".join(map(str, open_ports)),
            "Alert Count": alert_count,
        })

    csv_path = "reports/network_report.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["IP", "MAC", "Vendor", "Open Ports", "Alert Count"]
        )
        writer.writeheader()
        writer.writerows(report_rows)

    score_color = {
        "CRITICAL": "#e83030",
        "HIGH":     "#ff6b35",
        "MEDIUM":   "#ffa500",
        "LOW":      "#3498db",
        "MINIMAL":  "#2ecc71",
    }.get(label, "#adb3c0")

    rows_html = ""
    for row in report_rows:
        rows_html += f"""
        <tr>
          <td>{row['IP']}</td>
          <td style="font-size:12px;color:#adb3c0">{row['MAC']}</td>
          <td style="color:#e83030">{row['Vendor']}</td>
          <td>{row['Open Ports'] or '—'}</td>
          <td>{row['Alert Count']}</td>
        </tr>"""

    alert_rows_html = ""
    for a in sorted(alerts, key=lambda x: x.get("time",""), reverse=True)[:20]:
        sev = a.get("severity","INFO")
        col = {"CRITICAL":"#e83030","HIGH":"#ff6b35","MEDIUM":"#ffa500",
               "LOW":"#3498db","INFO":"#2ecc71"}.get(sev,"#adb3c0")
        alert_rows_html += f"""
        <tr>
          <td><span style="color:{col};font-weight:700">{sev}</span></td>
          <td>{a.get('message','')}</td>
          <td style="color:#484f5e;font-size:12px">{a.get('time','')}</td>
        </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Network Security Report — {generated_at}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{--red:#e83030;--bg:#040608;--surface:#080a0f;--surface2:#0c0e15;
         --border:#181b24;--text:#adb3c0;--dim:#484f5e;--white:#e8eaf0;}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;padding:40px 48px;}}
  h1{{font-family:'Inter',sans-serif;font-size:22px;font-weight:800;color:var(--white);letter-spacing:1px;margin-bottom:4px;}}
  .meta{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--dim);letter-spacing:2px;margin-bottom:32px;}}
  .risk-box{{display:inline-flex;align-items:center;gap:20px;background:var(--surface);
             border:1px solid {score_color};border-radius:4px;padding:20px 32px;margin-bottom:36px;}}
  .risk-score{{font-family:'Inter',sans-serif;font-size:48px;font-weight:800;
               color:{score_color};text-shadow:0 0 16px {score_color}44;line-height:1;}}
  .risk-label{{font-family:'JetBrains Mono',monospace;font-size:13px;color:{score_color};
               letter-spacing:2px;margin-top:4px;}}
  .risk-detail{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--dim);line-height:1.8;}}
  h2{{font-family:'Inter',sans-serif;font-size:14px;font-weight:700;color:var(--red);
      text-transform:uppercase;letter-spacing:3px;margin-bottom:10px;padding-bottom:6px;
      border-bottom:1px solid rgba(232,48,48,0.15);}}
  .section{{margin-bottom:36px;}}
  table{{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--border);
         border-radius:3px;overflow:hidden;margin-top:4px;}}
  th{{font-family:'Inter',sans-serif;font-size:12px;font-weight:600;color:rgba(232,48,48,0.8);
      text-transform:uppercase;letter-spacing:2px;padding:12px 18px;text-align:left;
      background:var(--surface2);border-bottom:1px solid rgba(232,48,48,0.15);}}
  td{{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--text);
      padding:12px 18px;border-bottom:1px solid rgba(255,255,255,0.025);}}
  tr:last-child td{{border-bottom:none;}}
  .footer{{margin-top:40px;font-family:'JetBrains Mono',monospace;font-size:10px;
           color:var(--dim);letter-spacing:2px;border-top:1px solid var(--border);padding-top:16px;}}
</style>
</head>
<body>
<h1>🛡 HOME NETWORK SECURITY REPORT</h1>
<div class="meta">// Generated: {generated_at} &nbsp;·&nbsp; Home Network Security Monitor</div>

<div class="risk-box">
  <div>
    <div class="risk-score">{risk['score']}/100</div>
    <div class="risk-label">RISK: {label}</div>
  </div>
  <div class="risk-detail">
    Port component &nbsp;: {risk['port_score']}/50 ({risk['open_port_count']} open ports)<br>
    Alert component: {risk['alert_score']}/50 ({risk['alert_count']} alerts)
  </div>
</div>

<div class="section">
  <h2>Device Inventory</h2>
  <table>
    <thead><tr><th>IP Address</th><th>MAC Address</th><th>Vendor</th><th>Open Ports</th><th>Alerts</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>

<div class="section">
  <h2>Recent Alerts (last 20)</h2>
  <table>
    <thead><tr><th>Severity</th><th>Message</th><th>Timestamp</th></tr></thead>
    <tbody>{alert_rows_html if alert_rows_html else '<tr><td colspan="3" style="color:#484f5e;text-align:center">No alerts recorded</td></tr>'}</tbody>
  </table>
</div>

<div class="footer">Home Network Security Monitor &nbsp;·&nbsp; network_report &nbsp;·&nbsp; {generated_at}</div>
</body>
</html>"""

    html_path = "reports/network_report.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ CSV  report : {csv_path}")
    print(f"✓ HTML report : {html_path}")
    print(f"✓ Risk Score  : {risk['score']}/100  [{label}]")
    return risk


if __name__ == "__main__":
    generate_report()
