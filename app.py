from flask import Flask, render_template, redirect, url_for, flash
import json
import os

from vendor import enrich_devices
from risk_score import calculate_risk_score, risk_label
from reports import generate_report

app = Flask(__name__)
app.secret_key = "hnsm-secret-key"


def load_json(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception:
        return []


@app.route("/")
def dashboard():
    devices       = load_json("data/devices.json")
    alerts        = load_json("data/alerts.json")
    scans         = load_json("data/scan_history.json")
    stats_history = load_json("data/stats_history.json")
    device_history= load_json("data/device_history.json")

    devices = enrich_devices(devices)

    total_devices = len(devices)
    total_alerts  = len(alerts)
    total_ports   = 0
    port_data     = []

    for device in scans:
        ip = device.get("ip")
        for port in device.get("open_ports", []):
            total_ports += 1
            port_data.append({"ip": ip, "port": port})

    recent_alerts = sorted(
        alerts, key=lambda x: x.get("time", ""), reverse=True
    )[:10]

    risk     = calculate_risk_score()
    rlabel   = risk_label(risk["score"])

    return render_template(
        "dashboard.html",
        devices=devices,
        total_devices=total_devices,
        total_alerts=total_alerts,
        total_ports=total_ports,
        port_data=port_data,
        alerts=recent_alerts,
        stats_history=stats_history,
        device_history=device_history,
        risk=risk,
        risk_label=rlabel,
    )


@app.route("/generate-report")
def generate_report_route():
    try:
        generate_report()
        flash("✓ Report generated successfully in the reports/ directory.", "success")
    except Exception as e:
        flash(f"✗ Report generation failed: {e}", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
