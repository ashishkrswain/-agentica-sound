from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
TRACKS_DIR = STORAGE_DIR / "tracks"
MODELS_DIR = STORAGE_DIR / "models"
DB_PATH = STORAGE_DIR / "agentica_sound.db"
FRONTEND_DIR = BASE_DIR / "frontend"

# Server
HOST = "127.0.0.1"
PORT = 8000

# Auth
SECRET_KEY = "agentica-sound-secret-key-music-studio-2026"
DEFAULT_USER = "ashish_local"
DEFAULT_PASS = "sound2026"

# Audio defaults
SAMPLE_RATE = 44100
DEFAULT_DURATION = 30  # seconds
MAX_DURATION = 360     # up to 6 minutes
DEFAULT_BPM = 120

# Hardware Execution Modes
HARDWARE_MODES = {
    "hybrid": "Hybrid Offload (GPU + CPU + System RAM)",
    "gpu_only": "Dedicated GPU (NVIDIA GTX 1650 FP16)",
    "cpu_only": "CPU Multithread & RAM (No VRAM)",
    "neural_synth": "High-Fi Neural Synth (Zero Overhead)"
}

# LLM & Musical Intelligence Defaults
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_LM_STUDIO_URL = "http://127.0.0.1:1234/v1"
DEFAULT_NVIDIA_URL = "https://integrate.api.nvidia.com/v1"
