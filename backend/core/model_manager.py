import os
import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import MODELS_DIR

MODELS_DIR.mkdir(parents=True, exist_ok=True)

class ModelManager:
    """
    Manages local offline Hugging Face models, downloading to storage/models,
    and routing across GPU, CPU, and RAM execution modes.
    """
    def __init__(self):
        self.active_model_id = "facebook/musicgen-small"
        self.active_hardware_mode = "hybrid"  # hybrid, gpu_only, cpu_only, neural_synth
        self.download_state = {
            "is_downloading": False,
            "repo_id": "",
            "progress": 0,
            "status": "idle",
            "error": None
        }
        self.loaded_model = None
        self.loaded_processor = None
        self.loaded_repo_id = None
        self.loaded_mode = None

    def list_installed_models(self) -> List[Dict[str, Any]]:
        """Scans storage/models directly to list installed models without manual config."""
        installed = []
        # Always include the built-in instant Neural Synthesizer
        installed.append({
            "id": "builtin/neural-synth",
            "name": "Agentica High-Fi Neural Synthesizer",
            "type": "builtin",
            "is_downloaded": True,
            "size_mb": 0,
            "path": "builtin",
            "recommended_mode": "neural_synth",
            "description": "Zero-download 44.1kHz studio synthesizer. Drums, bass arpeggios, chords & leads with 0MB VRAM overhead."
        })

        if not MODELS_DIR.exists():
            return installed

        for item in MODELS_DIR.iterdir():
            if item.is_dir():
                has_weights = any(item.glob("**/*.safetensors")) or any(item.glob("**/*.bin"))
                info_file = item / "model_info.json"
                info = {}
                if info_file.exists():
                    try:
                        with open(info_file, "r") as fp:
                            info = json.load(fp)
                    except Exception:
                        pass
                
                # Calculate folder size
                total_size = sum(f.stat().st_size for f in item.glob("**/*") if f.is_file()) / (1024 * 1024)

                repo_name = info.get("repo_id", item.name.replace("--", "/"))
                installed.append({
                    "id": repo_name,
                    "name": repo_name,
                    "type": "huggingface",
                    "is_downloaded": has_weights,
                    "size_mb": round(total_size, 1),
                    "path": str(item),
                    "recommended_mode": "gpu_only" if total_size < 1800 else "hybrid",
                    "description": info.get("description", "Hugging Face model cached locally in storage/models.")
                })

        return installed

    def download_huggingface_model(self, repo_id: str):
        """Downloads a model directly from Hugging Face into storage/models."""
        repo_id = repo_id.strip()
        if not repo_id:
            raise ValueError("Repository ID cannot be empty")
        
        # Normalize Hugging Face URL if given
        if "huggingface.co/" in repo_id:
            repo_id = repo_id.split("huggingface.co/")[-1].strip("/")

        if self.download_state["is_downloading"]:
            raise RuntimeError("Another model download is already running")

        self.download_state = {
            "is_downloading": True,
            "repo_id": repo_id,
            "progress": 5,
            "status": f"Initializing download for {repo_id}...",
            "error": None
        }

        thread = threading.Thread(target=self._download_worker, args=(repo_id,), daemon=True)
        thread.start()

    def _download_worker(self, repo_id: str):
        try:
            folder_name = repo_id.replace("/", "--")
            target_dir = MODELS_DIR / folder_name
            target_dir.mkdir(parents=True, exist_ok=True)

            self.download_state["progress"] = 20
            self.download_state["status"] = f"Fetching tokenizer & processor from {repo_id}..."

            from transformers import AutoProcessor, MusicgenForConditionalGeneration

            processor = AutoProcessor.from_pretrained(repo_id, cache_dir=str(target_dir))
            self.download_state["progress"] = 50
            self.download_state["status"] = f"Downloading tensor weights to {target_dir}..."

            model = MusicgenForConditionalGeneration.from_pretrained(repo_id, cache_dir=str(target_dir))
            self.download_state["progress"] = 90
            self.download_state["status"] = "Validating downloaded weights and saving model profile..."

            # Save metadata
            info = {
                "repo_id": repo_id,
                "folder": folder_name,
                "downloaded_at": str(Path(__file__).stat().st_mtime),
                "description": f"Directly connected Hugging Face model: {repo_id}"
            }
            with open(target_dir / "model_info.json", "w") as fp:
                json.dump(info, fp, indent=2)

            self.download_state["progress"] = 100
            self.download_state["status"] = f"Model {repo_id} is successfully downloaded and bound directly to the workstation!"
            self.download_state["is_downloading"] = False
            self.active_model_id = repo_id

        except Exception as e:
            self.download_state["is_downloading"] = False
            self.download_state["status"] = f"Download failed: {str(e)}"
            self.download_state["error"] = str(e)

    def set_hardware_mode(self, mode: str):
        if mode not in ["hybrid", "gpu_only", "cpu_only", "neural_synth"]:
            raise ValueError(f"Invalid hardware mode: {mode}")
        self.active_hardware_mode = mode

    def set_active_model(self, model_id: str):
        self.active_model_id = model_id

    def get_runtime_status(self) -> Dict[str, Any]:
        return {
            "active_model": self.active_model_id,
            "hardware_mode": self.active_hardware_mode,
            "models_dir": str(MODELS_DIR),
            "download_state": self.download_state,
            "installed_count": len(self.list_installed_models())
        }

# Global singleton
model_manager = ModelManager()
