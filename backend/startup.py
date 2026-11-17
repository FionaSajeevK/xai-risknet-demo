"""
Startup helper for XAI-RiskNet Demo.
Prints both interface URLs and validates Telegram config before launching.
"""
import os
import sys
import subprocess
import socket

def get_local_ip():
    """Get the machine's local network IP for LAN access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def check_telegram():
    token = os.environ.get("TELEGRAM_TOKEN", "")
    chat  = os.environ.get("TELEGRAM_CHAT_ID", "")
    if token and chat:
        print("  ✅ Telegram : CONFIGURED  (alerts will be sent for real)")
    else:
        missing = []
        if not token:
            missing.append("TELEGRAM_TOKEN")
        if not chat:
            missing.append("TELEGRAM_CHAT_ID")
        print(f"  ⚠️  Telegram : NOT configured — {', '.join(missing)} not set.")
        print("       Alerts will run in SIMULATED mode (logged to alerts_log.jsonl).")
        print()
        print("  To enable real Telegram alerts, set these env vars before running:")
        print("    $env:TELEGRAM_TOKEN  = '<your-bot-token>'")
        print("    $env:TELEGRAM_CHAT_ID = '<your-chat-id>'")
        print("  Then restart this script.")

def main():
    port = int(os.environ.get("PORT", 8000))
    local_ip = get_local_ip()

    print()
    print("=" * 60)
    print("  🏔️   XAI-RiskNet Demo  —  Landslide Risk Assessment")
    print("=" * 60)
    print()
    print("  📡  Interfaces:")
    print()
    print(f"  🏛️  Authority Dashboard  →  http://127.0.0.1:{port}/")
    print(f"                              http://{local_ip}:{port}/")
    print()
    print(f"  🏠  Resident Interface   →  http://127.0.0.1:{port}/resident.html")
    print(f"                              http://{local_ip}:{port}/resident.html")
    print()
    print("  (Use the LAN address to open on another device on the same Wi-Fi)")
    print()
    print("  🔔  Telegram Alert Bot:")
    check_telegram()
    print()
    print("=" * 60)
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)
    print()

    # Launch uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--reload"
    ]
    try:
        subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n  Server stopped.")

if __name__ == "__main__":
    main()
