"""
WalkBacker Runner
Launches the offline FastAPI server with automatic host and port resolution.
"""
import uvicorn
from backend.config import HOST, PORT

if __name__ == "__main__":
    print(f"🌿 Starting WalkBacker (Touch Grass Open-Source AI)...")
    print(f"🚀 Server listening on http://{HOST}:{PORT}")
    print(f"💡 Designed for 8GB RAM devices. Zero cloud dependencies.")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False, log_level="info")
