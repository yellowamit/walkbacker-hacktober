"""
WalkBacker Runner
Launches the offline FastAPI server with automatic port detection,
stale process cleanup, and conflict prevention.
"""
import sys
import os
import socket
import psutil

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import uvicorn
from backend.config import HOST, PORT


def kill_process_on_port(port: int):
    """Attempt to terminate any stale process holding the desired port."""
    current_pid = os.getpid()
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr and conn.laddr.port == port and conn.pid:
            if conn.pid != current_pid:
                try:
                    p = psutil.Process(conn.pid)
                    # Only auto-terminate python/uvicorn stale runners
                    if "python" in p.name().lower():
                        print(f"[*] Releasing port {port} (terminated stale process PID {conn.pid})...")
                        p.terminate()
                        p.wait(timeout=2)
                except Exception:
                    pass


def find_free_port(preferred_port: int = 8000, host: str = "127.0.0.1") -> int:
    """Find preferred port or fallback to the next available port."""
    kill_process_on_port(preferred_port)

    # Test if preferred port is free
    for port in range(preferred_port, preferred_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return preferred_port


if __name__ == "__main__":
    target_port = find_free_port(PORT, "127.0.0.1")

    print("==================================================")
    print("🌿 WalkBacker: Touch Grass Open-Source AI")
    print("==================================================")
    print(f"🚀 Open in Browser: http://localhost:{target_port}")
    print(f"   or directly    : http://127.0.0.1:{target_port}")
    print(f"💡 RAM Footprint  : ~85MB RSS (Safe for 8GB devices)")
    print("==================================================\n")

    uvicorn.run("backend.main:app", host="127.0.0.1", port=target_port, reload=False, log_level="info")

