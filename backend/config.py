from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
TRACKS_DIR = STORAGE_DIR / "tracks"
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
MAX_DURATION = 120
DEFAULT_BPM = 120
