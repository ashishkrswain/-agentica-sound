import os
import threading
from pathlib import Path
from fastapi import APIRouter
from backend.config import STORAGE_DIR
from backend.core.musicgen_loader import musicgen_engine

router = APIRouter(prefix="/api/models", tags=["models"])

MODELS_DIR = STORAGE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

download_state = {
    "is_downloading": False,
    "progress": 0,
    "status": "idle",
    "error": None
}

def _download_worker():
    global download_state
    try:
        download_state["is_downloading"] = True
        download_state["status"] = "Connecting to Hugging Face Hub (facebook/musicgen-small)..."
        download_state["progress"] = 15

        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        
        # Download and cache into local project directory
        cache_path = str(MODELS_DIR)
        download_state["status"] = "Downloading model weights & tokenizer (~1.2 GB)..."
        download_state["progress"] = 45

        processor = AutoProcessor.from_pretrained("facebook/musicgen-small", cache_dir=cache_path)
        download_state["progress"] = 75
        download_state["status"] = "Validating transformer tensor weights..."

        model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small", cache_dir=cache_path)
        download_state["progress"] = 100
        download_state["status"] = "Weights successfully cached locally in storage/models."
        download_state["is_downloading"] = False

    except Exception as e:
        download_state["is_downloading"] = False
        download_state["status"] = f"Download error: {str(e)}"
        download_state["error"] = str(e)

@router.get("/status")
def get_model_status():
    model_cached = any(MODELS_DIR.glob("**/*.safetensors")) or any(MODELS_DIR.glob("**/*.bin"))
    return {
        "is_cached": model_cached,
        "models_dir": str(MODELS_DIR),
        "download_state": download_state,
        "engine_status": musicgen_engine.get_status()
    }

@router.post("/download")
def start_model_download():
    global download_state
    if download_state["is_downloading"]:
        return {"success": False, "message": "Download is already in progress"}
    
    download_state["error"] = None
    thread = threading.Thread(target=_download_worker, daemon=True)
    thread.start()
    return {"success": True, "message": "Model download initiated in background"}
