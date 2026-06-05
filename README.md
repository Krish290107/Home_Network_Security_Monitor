<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Scapy-FF6600?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Nmap-2B7A78?style=for-the-badge&logo=gnu-bash&logoColor=white"/>
<img src="https://img.shields.io/badge/status-active-brightgreen?style=for-the-badge"/>

<br/><br/>

# 🛡️ Home Network Security Monitor

**Know exactly what's on your network — and get alerted when something shouldn't be.**

*A Python tool that watches your home network 24/7, scores its risk level, and gives you a clean dashboard to see it all at a glance.*

[Features](#-what-it-does) · [Quick Start](#-quick-start) · [Dashboard](#-the-dashboard) · [How It Works](#-how-it-works) · [Risk Score](#-risk-score) · [Roadmap](#-roadmap)

</div>

---

## The Problem It Solves

Your home router has a device list buried somewhere in its admin panel. Most people never open it. And even if you do, it won't tell you when a new device connected at 3am, which ports are exposed, or how risky your current network state actually is.

This project fixes that. It runs in the background, scans your network regularly, and surfaces everything on a single dark-themed dashboard — no cloud account, no subscription, no data leaving your house.

---

## ✨ What It Does

**Device Discovery** — Uses ARP scanning to find every device on your subnet, from your phone to your smart TV to that Raspberry Pi you forgot about.

**Port Scanning** — Runs Nmap against each discovered device to map open ports. Finds things like exposed RDP, open databases, or Telnet that really shouldn't be there.

**Intrusion Alerts** — The moment an unrecognized device joins your network, you get a `HIGH` severity alert with its IP and MAC address. No polling required — the scheduler catches it automatically.

**5-Level Severity Engine** — Alerts are graded `INFO → LOW → MEDIUM → HIGH → CRITICAL` based on what triggered them. A new HTTPS port is not the same threat as an exposed Telnet port, and the system treats them differently.

**Live Risk Score** — A 0–100 score that combines your open-port exposure and active alert count into one honest number. It updates every scan cycle.

**Report Generation** — One click (or one command) generates a full CSV and HTML report of your network state — devices, ports, vendors, alert counts, and risk score all in one file.

**Historical Graphs** — Tracks device count, open ports, and alert volume over time so you can see trends, not just snapshots.

---

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:
- Python 3.9 or higher
- [Nmap](https://nmap.org/download.html) installed on your machine
- **Windows only:** [Npcap](https://npcap.com/) — Scapy needs it for raw packet capture

### 1. Clone and enter the project

```bash
git clone https://github.com/Krish290107/Home_Network_Security_Monitor.git
cd Home_Network_Security_Monitor
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate it:
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Nmap path

```bash
cp .env.example .env
```

Open `.env` and set the path to your Nmap binary:

```env
# Windows
NMAP_PATH=C:\Program Files\Nmap\nmap.exe

# macOS / Linux
NMAP_PATH=/usr/bin/nmap
```

### 5. Start monitoring

```bash
# Run as Administrator (Windows) or with sudo (Linux/macOS)
# — raw packet capture requires elevated privileges

python scheduler.py
```

That's it. It'll start scanning immediately. Open the dashboard in a separate terminal:

```bash
python app.py
```

Then go to **http://127.0.0.1:5000** in your browser.

---

## 🖥️ The Dashboard

The dashboard auto-refreshes every 30 seconds and shows everything in one view:

| Section | What you see |
| --- | --- |
| **Stat Cards** | Live device count, total alerts, and open port count |
| **Risk Score Panel** | 0–100 score with a breakdown bar and a Generate Report button |
| **Device Inventory** | IP, MAC, and resolved vendor name for every known device |
| **Open Ports** | Every exposed port across all devices with service name and per-port risk level |
| **Device History** | When each device was first and last seen on your network |
| **Alert Feed** | The 10 most recent alerts, colour-coded by severity |
| **Trend Graph** | Historical chart of devices, ports, and alerts over time |

---

## ⚙️ How It Works

The project is split into focused modules that each do one thing:

```
scheduler.py          ← runs everything on a timer (no manual commands needed)
    │
    ├── scanner.py    ← ARP scan → finds devices on the subnet
    │       └── database.py   ← saves device inventory, fires alerts for new ones
    │
    ├── portscan.py   ← Nmap scan → finds open ports per device
    │       └── compare_ports.py  ← diffs against last scan, alerts on new ports
    │
    ├── history.py    ← logs first/last seen timestamps per device
    ├── stats.py      ← records a snapshot (devices, ports, alerts) each cycle
    └── alerts.py     ← writes severity-graded alerts to disk

app.py                ← Flask server serving the dashboard at :5000
risk_score.py         ← calculates the 0–100 risk score on demand
reports.py            ← generates CSV + HTML reports
vendor.py             ← looks up MAC prefixes → manufacturer names (offline OUI DB)
```

**Scan intervals** (configurable in `scheduler.py`):
- Network scan: every **60 seconds**
- Port scan: every **5 minutes** (starts 30 seconds after launch to let device discovery run first)

---

## 🎯 Risk Score

The risk score gives you a single number that answers *"how exposed is my network right now?"*

It's calculated from two components:

```
Risk Score (0–100) = Port Risk (0–50) + Alert Risk (0–50)
```

**Port Risk** weights each open port by how dangerous it tends to be in practice:

| Port | Service | Weight |
| --- | --- | --- |
| 23 | Telnet | 5 / 5 |
| 445 | SMB | 5 / 5 |
| 3389 | RDP | 5 / 5 |
| 5900 | VNC | 5 / 5 |
| 21 | FTP | 5 / 5 |
| 22 | SSH | 3 / 5 |
| 3306 | MySQL | 4 / 5 |
| 80 | HTTP | 2 / 5 |
| 443 | HTTPS | 1 / 5 |

**Alert Risk** weights each active alert by its severity level:

| Severity | Weight |
| --- | --- |
| CRITICAL | 10 |
| HIGH | 6 |
| MEDIUM | 3 |
| LOW | 1 |
| INFO | 0 |

**Score labels:**

| Score | Label | What it means |
| --- | --- | --- |
| 0 – 19 | 🟢 MINIMAL | Clean network, nothing concerning |
| 20 – 39 | 🔵 LOW | Minor exposure, worth a look |
| 40 – 59 | 🟡 MEDIUM | Some risky ports or active alerts |
| 60 – 79 | 🔴 HIGH | Significant exposure — investigate |
| 80 – 100 | ⛔ CRITICAL | Serious risk — act now |

---

## 📂 Project Structure

```
Home_Network_Security_Monitor/
│
├── app.py               # Flask web server and dashboard routes
├── scheduler.py         # Background thread manager (runs all scans automatically)
├── scanner.py           # ARP network scanner — finds devices on your subnet
├── portscan.py          # Nmap port scanner — probes each device for open ports
├── compare_ports.py     # Diffs current vs. previous port scan, fires alerts on changes
├── database.py          # Manages the device inventory JSON file
├── history.py           # Tracks first/last-seen timestamps per device
├── alerts.py            # 5-level severity alert engine
├── risk_score.py        # Calculates the 0–100 network risk score
├── vendor.py            # Offline MAC → manufacturer lookup (OUI database)
├── stats.py             # Records periodic snapshots for the trend graph
├── reports.py           # Generates CSV and HTML reports
│
├── templates/
│   └── dashboard.html   # The main dashboard UI
│
├── data/                # All runtime data lives here (JSON files)
│   ├── devices.json
│   ├── alerts.json
│   ├── scan_history.json
│   ├── device_history.json
│   └── stats_history.json
│
├── reports/             # Generated reports end up here
│   ├── network_report.csv
│   └── network_report.html
│
├── .env.example         # Copy this to .env and set your Nmap path
└── requirements.txt
```

---

## 🕹️ Running Things Manually

The scheduler handles everything automatically, but you can also run individual pieces:

```bash
# Discover devices on your network
python scanner.py

# Scan open ports on known devices
python portscan.py

# Print the current risk score to the terminal
python risk_score.py

# Generate a full report (CSV + HTML)
python reports.py
```

---

## 🛠️ Tech Stack

| Tool | Why |
| --- | --- |
| **Python 3** | The whole backbone — scripting, threading, HTTP server |
| **Scapy** | Sends and parses ARP packets for device discovery |
| **Nmap + python-nmap** | Port scanning with real network intelligence |
| **Flask** | Serves the dashboard; lightweight and zero-config |
| **Chart.js** | Draws the historical trend graph in the browser |
| **JSON files** | Dead-simple persistence — no database setup required |

---

## ⚠️ A Note on Permissions

Network scanning requires elevated privileges because it uses raw packets:

- **Linux / macOS** — run with `sudo`
- **Windows** — run your terminal as Administrator

The web dashboard (`app.py`) doesn't need elevated privileges and can run as a normal user.

This tool is intended for use on networks you own or have explicit permission to monitor.

---

<div align="center">

Built by **Krish** — because curiosity about what's on your own network is a feature, not a bug.


</div>