import os
import secrets
from dotenv import load_dotenv, set_key
from flask import Flask, flash, redirect, render_template, url_for
import storage
from reports import generate_report
from risk_score import calculate_risk_score, risk_label
from vendor import enrich_devices
ENV_PATH = os.path.join(storage.BASE_DIR, '.env')
load_dotenv(ENV_PATH)
app = Flask(__name__)

def _get_or_create_secret_key():
    key = os.getenv('FLASK_SECRET_KEY')
    if key:
        return key
    key = secrets.token_hex(32)
    try:
        set_key(ENV_PATH, 'FLASK_SECRET_KEY', key)
        print(f'Generated a new FLASK_SECRET_KEY and saved it to {ENV_PATH}')
    except OSError as error:
        print(f'WARNING: could not save FLASK_SECRET_KEY to .env ({error}). A new key will be generated on every restart until this is fixed.')
    return key
app.secret_key = _get_or_create_secret_key()

def _flag(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ('1', 'true', 'yes', 'on')

@app.route('/')
def dashboard():
    with storage.LOCK:
        devices = storage.load_list(storage.DEVICES_FILE)
        alerts = storage.load_list(storage.ALERTS_FILE)
        scans = storage.load_list(storage.SCAN_HISTORY_FILE)
        stats_history = storage.load_list(storage.STATS_FILE)
        device_history = storage.load_list(storage.DEVICE_HISTORY_FILE)
        risk = calculate_risk_score()
    devices = enrich_devices(devices)
    port_data = []
    for scan in scans:
        ip = scan.get('ip')
        for port in scan.get('open_ports', []):
            try:
                port_data.append({'ip': ip, 'port': int(port)})
            except (TypeError, ValueError):
                continue
    recent_alerts = sorted(alerts, key=lambda alert: alert.get('time', ''), reverse=True)[:10]
    return render_template('dashboard.html', devices=devices, total_devices=len(devices), total_alerts=len(alerts), total_ports=len(port_data), port_data=port_data, alerts=recent_alerts, stats_history=stats_history, device_history=device_history, risk=risk, risk_label=risk_label(risk['score']))

@app.route('/generate-report', methods=['POST'])
def generate_report_route():
    try:
        generate_report()
        flash('Report generated in the reports/ directory.', 'success')
    except Exception as error:
        app.logger.exception('Report generation failed')
        flash(f'Report generation failed: {error}', 'error')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found(_error):
    return redirect(url_for('dashboard'))
if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST', '127.0.0.1'), port=int(os.getenv('FLASK_PORT', '5000')), debug=_flag('FLASK_DEBUG', False))
