"""
WalkBacker Runner
Launches the offline FastAPI server with automatic host and port resolution.
Automatically opens your browser to the correct local address (http://localhost:8000)
and displays the exact network address for your phone.
"""
import sys
import os
import socket
import threading
import time
import webbrowser

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import uvicorn
from backend.config import PORT


def get_lan_ip() -> str:
    """Discovers the laptop's local LAN IP for phone access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def is_port_in_use(port: int) -> bool:
    """Check if the target port is already occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def open_browser(url: str):
    """Wait for uvicorn to bind and open browser automatically."""
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass


if __name__ == "__main__":
    target_port = PORT
    if is_port_in_use(target_port):
        # Check if 8000 is in use, switch to 8001 if needed
        print(f"[!] Notice: Port {target_port} is currently in use. Trying port 8001...")
        target_port = 8001

    lan_ip = get_lan_ip()
    local_url = f"http://localhost:{target_port}"
    lan_url = f"http://{lan_ip}:{target_port}"

    print("=" * 64)
    print("🌿 WalkBacker: Touch Grass Open-Source AI Expedition Agent")
    print("=" * 64)
    print(f"💻 On this laptop, open:")
    print(f"   👉 {local_url}   (or http://127.0.0.1:{target_port})")
    print(f"\n📱 On your mobile phone (same Wi-Fi), open:")
    print(f"   👉 {lan_url}")
    print(f"\n🌐 GitHub Pages (HTTPS PWA for phone in the woods):")
    print(f"   👉 https://yellowamit.github.io/walkbacker-hacktober/")
    print("=" * 64)
    print("[*] Note: Do NOT open 'http://0.0.0.0' in your browser — Windows")
    print("    treats 0.0.0.0 as invalid. Always use http://localhost:8000\n")

    # Launch browser automatically to localhost
    threading.Thread(target=open_browser, args=(local_url,), daemon=True).start()

    # Listen on 0.0.0.0 so phone on LAN can reach it, while laptop accesses localhost
    uvicorn.run("backend.main:app", host="0.0.0.0", port=target_port, reload=False, log_level="info")
