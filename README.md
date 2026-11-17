# XAI-RiskNet Demo 🏔️
> **Landslide Risk Assessment — Prototype**  
> Study area: Meppadi, Wayanad, Kerala

A demonstration system with two interfaces — one for **authorities** and one for **residents** — with Telegram bot integration for alert delivery.

---

## Interfaces

| Interface | URL |
|---|---|
| 🏛️ Authority Dashboard | `http://localhost:8000/` |
| 🏠 Resident Alert View | `http://localhost:8000/resident.html` |

---

## Features

- **Risk map** — slope-based landslide risk layer driven by rainfall inputs
- **Rainfall scenarios** — Dry / Heavy / Very Heavy / Extreme
- **CAP alert messages** — Common Alerting Protocol XML generation
- **Evacuation routing** — shortest + safest route to nearest shelter
- **Telegram alerts** — real-time bot notification (configurable)
- **Bilingual UI** — English and Malayalam (resident interface)

---

## Setup

### 1. Create a virtual environment and install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. (Optional) Configure Telegram alerts

Create a bot via [@BotFather](https://t.me/BotFather) on Telegram and get:
- **Bot token** — given by BotFather after creating a bot
- **Chat ID** — visit `https://api.telegram.org/bot<TOKEN>/getUpdates` after messaging your bot

Set the environment variables before starting the server:

```powershell
# PowerShell
$env:TELEGRAM_TOKEN   = "123456789:ABCdef-your-token"
$env:TELEGRAM_CHAT_ID = "987654321"
```

```bash
# bash / zsh
export TELEGRAM_TOKEN="123456789:ABCdef-your-token"
export TELEGRAM_CHAT_ID="987654321"
```

> Without these, the system runs in **SIMULATED** mode — alerts are logged to `backend/data/alerts_log.jsonl` but nothing is sent.

### 3. Start the server

```bash
cd backend
python startup.py
```

The terminal will print both interface URLs and show the Telegram status.

---

## Project Structure

```
xai-risknet-demo/
├── backend/
│   ├── app.py          # FastAPI application & API routes
│   ├── alerts.py       # Telegram dispatch & alert logging
│   ├── cap.py          # CAP (Common Alerting Protocol) builder
│   ├── messages.py     # Alert text generation
│   ├── risk.py         # Risk model (slope + rainfall)
│   ├── routing.py      # Evacuation route calculation
│   ├── startup.py      # Launch helper (prints URLs, checks Telegram)
│   └── data/           # GeoTIFF, GeoJSON, road graph
├── frontend/
│   ├── index.html      # Authority dashboard
│   └── resident.html   # Resident alert interface
└── requirements.txt
```

---

## Tech Stack

- **Backend** — FastAPI + Uvicorn
- **GIS** — Rasterio, GeoPandas, Shapely, OSMnx, NetworkX
- **Frontend** — Vanilla JS + Leaflet.js
- **Alerts** — Telegram Bot API, CAP XML

---

> ⚠️ **This is a prototype for demonstration purposes.** Risk data uses slope-based placeholders. Not intended for real emergency use.
