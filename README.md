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

[Features](#-what-it-does) · [Quick Start](#-quick-start) · [Configuration](#-configuration) · [What's Automated](#-whats-automated) · [Dashboard](#-the-dashboard) · [How It Works](#-how-it-works) · [Risk Score](#-risk-score) · [Project Structure](#-project-structure)

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

**Live Risk Score** — A 0–100 score that combines your open-port exposure and *recent* alert activity into one honest number. It updates every scan cycle and decays as old alerts age out, so it reflects your network's current state rather than its entire history.

**Report Generation** — One click (or one command) generates a full CSV and HTML report of your network state — devices, ports, vendors, alert counts, and risk score all in one file.

**Historical Graphs** — Tracks device count, open ports, and alert volume over time so you can see trends, not just snapshots.

---

## 🚀 Quick Start

### Prerequisites

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

source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Copy the environment template

```bash
cp .env.example .env
```

You can leave every value in `.env` blank. The app fills in sensible defaults and self-configures on first run — see [What's Automated](#-whats-automated) below. The only line you're likely to touch is `NMAP_PATH`, and only if Nmap isn't already on your system `PATH` (common on Windows):

```env
NMAP_PATH=C:\Program Files\Nmap\nmap.exe
```

### 5. Start monitoring

```bash
# Requires elevated privileges — raw packet capture needs it
sudo python scheduler.py        # macOS / Linux
python scheduler.py             # Windows, run terminal as Administrator
```

This starts scanning immediately. In a **second terminal**, start the dashboard:

```bash
source venv/bin/activate        # activate the same venv again
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> `app.py` doesn't touch the network and doesn't need elevated privileges — only `scheduler.py`/`scanner.py`/`portscan.py` do.

---

## 🤖 What's Automated

Nothing here needs manual setup beyond copying `.env.example` to `.env`. Specifically:

| Thing | How it's automated |
| --- | --- |
| **Flask session secret key** | Generated once on first run of `app.py` and written back into `.env` automatically. Every later run reads the same saved key, so sessions and flash messages survive restarts. If `.env` doesn't even exist yet, it gets created. Nothing to generate or paste in by hand. |
| **Network range to scan** | Auto-detected from your machine's local IP as a `/24` if `NETWORK_RANGE` is left blank in `.env`. Only set it yourself if you want to scan something other than your own subnet. |
| **Nmap binary location** | If `NMAP_PATH` is blank, the app looks for `nmap` on your system `PATH` automatically. Only set `NMAP_PATH` if that lookup would fail (typically Windows, where Nmap isn't added to `PATH` by default). |
| **Data & report folders** | `data/` and `reports/` are created automatically if missing — no manual `mkdir` needed. |
| **File paths** | All reads/writes resolve to absolute paths anchored at the project root, so it no longer matters which directory you launch a script from. |
| **New-port alert de-duplication** | Handled centrally by `compare_ports.py`, called automatically at the end of every port scan — you don't run it separately. |
| **Concurrent writes** | `scheduler.py` runs discovery and port scans on independent timers; all shared JSON state goes through one lock and atomic writes, so overlapping scans can't corrupt data — no manual coordination needed. |

In short: `cp .env.example .env`, then `sudo python scheduler.py` and `python app.py`. That's the entire setup.

---

## 🔧 Configuration

All configuration lives in `.env`. Every value is optional — see [What's Automated](#-whats-automated) for what fills in automatically when left blank.

| Variable | Default when blank | What it does |
| --- | --- | --- |
| `NETWORK_RANGE` | auto-detected local `/24` | CIDR range to scan, e.g. `192.168.1.0/24`. |
| `NMAP_PATH` | `nmap` found on `PATH` | Full path to the Nmap binary. Set only if Nmap isn't on `PATH`. |
| `NETWORK_SCAN_INTERVAL` | `60` | Seconds between ARP device-discovery scans. |
| `PORT_SCAN_INTERVAL` | `300` | Seconds between Nmap port scans. |
| `FLASK_SECRET_KEY` | auto-generated on first run | Signing key for session cookies. Leave blank — see [What's Automated](#-whats-automated). |
| `FLASK_HOST` | `127.0.0.1` | Interface the dashboard binds to. |
| `FLASK_PORT` | `5000` | Port the dashboard binds to. |
| `FLASK_DEBUG` | `false` | Flask debug mode. Keep off outside local development — it exposes a remote code-execution console on error pages. |

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
storage.py            ← shared JSON persistence: absolute paths, atomic writes, one lock
risk_score.py         ← calculates the 0–100 risk score on demand
reports.py            ← generates CSV + HTML reports
vendor.py             ← looks up MAC prefixes → manufacturer names (offline OUI DB)
```

**Scan intervals** default to a network scan every **60 seconds** and a port scan every **5 minutes** (starting 30 seconds after launch, so device discovery runs first). Both are configurable — see [Configuration](#-configuration).

---

## 🎯 Risk Score

```
Risk Score (0–100) = Port Risk (0–50) + Alert Risk (0–50)
```

**Port Risk** weights each currently-open port by how dangerous it tends to be in practice:

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

**Alert Risk** weights each alert from the **last 24 hours** by severity — older alerts age out automatically:

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
├── app.py               # Flask web server, dashboard routes, secret-key automation
├── scheduler.py         # Background thread manager (runs all scans automatically)
├── scanner.py           # ARP network scanner — finds devices on your subnet
├── portscan.py          # Nmap port scanner — probes each device for open ports
├── compare_ports.py     # Diffs current vs. previous port scan, fires alerts on changes
├── database.py          # Manages the device inventory JSON file
├── history.py           # Tracks first/last-seen timestamps per device
├── alerts.py             # 5-level severity alert engine
├── risk_score.py        # Calculates the 0–100 network risk score
├── vendor.py             # Offline MAC → manufacturer lookup (OUI database)
├── stats.py              # Records periodic snapshots for the trend graph
├── reports.py            # Generates CSV and HTML reports
├── storage.py            # Shared JSON persistence (paths, locking, atomic writes)
│
├── templates/
│   └── dashboard.html    # The main dashboard UI
│
├── data/                  # Runtime data (JSON), created automatically, gitignored
├── reports/               # Generated reports, created automatically, gitignored
│
├── .env.example           # Copy to .env — every value is optional
└── requirements.txt
```

---

## 🕹️ Running Things Manually

The scheduler handles everything automatically, but you can run individual pieces if you want to test something in isolation:

```bash
python scanner.py       # one ARP scan
python portscan.py      # one port scan (requires devices.json to exist first)
python risk_score.py    # print current risk score
python reports.py       # generate CSV + HTML report in reports/
```

You can also trigger a report straight from the dashboard via the **Generate Report** button.

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

## 🔒 A Note on Data

`data/*.json` holds your real device inventory — IP addresses, MAC addresses, and vendor names for everything on your network. It's excluded from git by `.gitignore` so it's never committed going forward. If you forked or cloned this project before that exclusion was added, check your git history for anything under `data/`.

---

<div align="center">

Built by **Krish** — because curiosity about what's on your own network is a feature, not a bug.

</div>
