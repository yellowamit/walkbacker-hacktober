"""
WalkBacker Configuration
Optimized for 8GB RAM devices and 100% offline edge execution.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "frontend"
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# Hardware & Memory Guardrails (Target: < 1.0 GB RAM for AI engine)
MAX_RAM_ALLOWANCE_MB = 1024
DEFAULT_MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"  # ~270MB safetensors, ultra-lightweight
FALLBACK_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

# Server Configuration
HOST = os.getenv("WALKBACKER_HOST", "0.0.0.0")
PORT = int(os.getenv("WALKBACKER_PORT", "8000"))

# Default Expedition Settings
DEFAULT_WALKING_SPEED_KMH = 4.5  # Average walking pace in nature
DEFAULT_SAFETY_FACTOR = 0.85     # Buffer for photography, stops, and navigation
DEFAULT_EXPEDITION_MINUTES = 45
