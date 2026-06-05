import json
import os

TOP_PORTS = {
    21:    {"service": "FTP",        "risk": 5},
    22:    {"service": "SSH",        "risk": 3},
    23:    {"service": "Telnet",     "risk": 5},
    25:    {"service": "SMTP",       "risk": 4},
    53:    {"service": "DNS",        "risk": 2},
    80:    {"service": "HTTP",       "risk": 2},
    135:   {"service": "MSRPC",      "risk": 4},
    139:   {"service": "NetBIOS",    "risk": 4},
    443:   {"service": "HTTPS",      "risk": 1},
    445:   {"service": "SMB",        "risk": 5},
    1433:  {"service": "MSSQL",      "risk": 4},
    1521:  {"service": "Oracle",     "risk": 4},
    3306:  {"service": "MySQL",      "risk": 4},
    3389:  {"service": "RDP",        "risk": 5},
    5432:  {"service": "PostgreSQL", "risk": 4},
    5900:  {"service": "VNC",        "risk": 5},
    6379:  {"service": "Redis",      "risk": 4},
    8080:  {"service": "HTTP-Alt",   "risk": 3},
    8443:  {"service": "HTTPS-Alt",  "risk": 2},
    27017: {"service": "MongoDB",    "risk": 5},
}

ALERT_WEIGHTS = {
    "CRITICAL": 10,
    "HIGH":      6,
    "MEDIUM":    3,
    "LOW":       1,
    "INFO":      0,
}


def _load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def calculate_risk_score():
    scans  = _load_json("data/scan_history.json")
    alerts = _load_json("data/alerts.json")

    port_score_raw = 0
    for device in scans:
        for port in device.get("open_ports", []):
            if port in TOP_PORTS:
                port_score_raw += TOP_PORTS[port]["risk"]
            else:
                port_score_raw += 1

    port_score = min(50, int((port_score_raw / 20) * 50))

    alert_score_raw = 0
    for alert in alerts:
        sev = alert.get("severity", "INFO").upper()
        alert_score_raw += ALERT_WEIGHTS.get(sev, 0)

    alert_score = min(50, int((alert_score_raw / 50) * 50))

    total = port_score + alert_score

    return {
        "score": total,
        "port_score": port_score,
        "alert_score": alert_score,
        "open_port_count": sum(len(d.get("open_ports", [])) for d in scans),
        "alert_count": len(alerts),
    }


def risk_label(score):
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    if score >= 20:
        return "LOW"
    return "MINIMAL"


if __name__ == "__main__":
    result = calculate_risk_score()
    label  = risk_label(result["score"])
    print(f"Risk Score : {result['score']}/100  [{label}]")
    print(f"  Port component  : {result['port_score']}/50  ({result['open_port_count']} open ports)")
    print(f"  Alert component : {result['alert_score']}/50  ({result['alert_count']} alerts)")
