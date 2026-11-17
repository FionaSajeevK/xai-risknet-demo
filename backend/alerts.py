import json
import os
from datetime import datetime
import requests

# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def _telegram_configured():
    """Return (token, chat_id) tuple, or (None, None) if not set."""
    return os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(text: str):
    """
    Send *text* via Telegram.

    Returns (ok: bool, detail: str).
    If the env-vars are missing the message is NOT sent and the caller
    should log the alert as SIMULATED.

    Setup:
        1. Create a bot with @BotFather -> copy the token.
        2. Start a chat with your bot, then visit:
               https://api.telegram.org/bot<TOKEN>/getUpdates
           to find your chat_id.
        3. Set env vars before launching (PowerShell example):
               $env:TELEGRAM_TOKEN   = "123456:ABC-your-token"
               $env:TELEGRAM_CHAT_ID = "987654321"
           Then run:  python startup.py   (from the backend/ folder)
    """
    token, chat = _telegram_configured()
    if not token or not chat:
        return False, "TELEGRAM_TOKEN / TELEGRAM_CHAT_ID not set"
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text},
            timeout=10,
        )
        if resp.ok:
            return True, "sent"
        # Hide token from error text
        return False, resp.text[:200].replace(token, "***")
    except requests.RequestException as exc:
        return False, str(exc).replace(token, "***")[:200]


def dispatch(log_path, level, cap_xml, text):
    ok, detail = send_telegram(text)
    mode = (
        "REAL - Telegram message sent to the configured phone"
        if ok
        else f"SIMULATED - nothing sent ({detail})"
    )
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "mode": mode,
        "message_preview": text[:120],
        "cap_bytes": len(cap_xml),
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
