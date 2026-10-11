"""
WalkBacker Runner
Launches the offline FastAPI server with automatic host and port resolution.
Safe for Windows cp1252 consoles.
"""
import sys
import io

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import uvicorn
from backend.config import HOST, PORT

if __name__ == "__main__":
    print(f"[*] Starting WalkBacker (Touch Grass Open-Source AI)...")
    print(f"[*] Server listening on http://{HOST}:{PORT}")
    print(f"[*] Optimized for 8GB RAM devices. Zero cloud dependencies.")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False, log_level="info")
