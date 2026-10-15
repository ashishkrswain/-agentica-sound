import os
import logging
from pathlib import Path
from typing import Optional, Tuple, List
import scipy.io.wavfile as wav
import numpy as np

from backend.config import MODELS_DIR, TRACKS_DIR, SAMPLE_RATE
from backend.core.audio_synth import generate_music_track, compute_waveform_peaks
from backend.core.model_manager import model_manager

logger = logging.getLogger(__name__)

class MusicGenEngine:
    """
    Adapter for Meta MusicGen via HuggingFace Transformers.
    Dynamically routes between locally downloaded weights in storage/models
    and the built-in High-Fi neural synthesizer depending on user hardware mode.
    """
    def __init__(self):
        self.loaded_model = None
        self.loaded_processor = None
        self.loaded_path = None
        self.device = "cpu"
        self._check_device()

    def _check_device(self):
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        except Exception:
            self.device = "cpu"

    def get_status(self) -> dict:
        return {
            "engine": "MusicGen (Meta AudioCraft/Transformers)",
            "device": self.device,
            "hardware_mode": model_manager.active_hardware_mode,
            "supports_cuda": self.device == "cuda",
            "active_model": model_manager.active_model_id
        }

    def _find_local_model_path(self, repo_id: str) -> Optional[Path]:
        """Looks for downloaded weights inside storage/models/."""
        if not MODELS_DIR.exists():
            return None
        folder_name = repo_id.replace("/", "--")
        target = MODELS_DIR / folder_name
        if target.exists() and (any(target.glob("**/*.safetensors")) or any(target.glob("**/*.bin"))):
            return target
        return None

    def generate(
        self,
        track_id: str,
        prompt: str,
        genre: str,
        bpm: int,
        duration_sec: float,
        seed: Optional[int] = None
    ) -> Tuple[str, List[float], float]:
        """
        Attempts to generate using downloaded HuggingFace model weights if present
        on local hardware; otherwise seamlessly falls back to high-fi studio synthesizer.
        """
        mode = model_manager.active_hardware_mode
        active_repo = model_manager.active_model_id
        local_path = self._find_local_model_path(active_repo)

        # If user selected neural_synth mode or weights aren't downloaded, use instant synth
        if mode == "neural_synth" or not local_path:
            return generate_music_track(
                track_id=track_id,
                title=prompt,
                genre=genre,
                bpm=bpm,
                duration_sec=duration_sec,
                seed=seed
            )

        # Attempt to run PyTorch inference on downloaded model weights
        try:
            import torch
            from transformers import AutoProcessor, MusicgenForConditionalGeneration

            if str(local_path) != self.loaded_path or self.loaded_model is None:
                logger.info(f"Loading MusicGen model from {local_path} (mode={mode})...")
                processor = AutoProcessor.from_pretrained(str(local_path))

                if mode == "gpu_only" and torch.cuda.is_available():
                    model = MusicgenForConditionalGeneration.from_pretrained(
                        str(local_path),
                        torch_dtype=torch.float16
                    ).to("cuda")
                elif mode == "hybrid" and torch.cuda.is_available():
                    # Offload: FP16 with attention accelerated on CUDA
                    model = MusicgenForConditionalGeneration.from_pretrained(
                        str(local_path),
                        torch_dtype=torch.float16,
                        device_map="auto"
                    )
                else:
                    # CPU multithreaded
                    model = MusicgenForConditionalGeneration.from_pretrained(
                        str(local_path),
                        torch_dtype=torch.float32
                    ).to("cpu")

                self.loaded_model = model
                self.loaded_processor = processor
                self.loaded_path = str(local_path)

            # Conditioning inputs
            full_prompt = f"{genre} style, {bpm} BPM, {prompt}"
            inputs = self.loaded_processor(
                text=[full_prompt],
                padding=True,
                return_tensors="pt"
            )

            target_device = "cuda" if (mode in ["gpu_only", "hybrid"] and torch.cuda.is_available()) else "cpu"
            if target_device == "cuda":
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            # Set max new tokens based on duration (approx 50 tokens per sec of audio)
            max_tokens = int(min(duration_sec, 30.0) * 50)
            if seed:
                torch.manual_seed(seed)

            with torch.no_grad():
                audio_values = self.loaded_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    guidance_scale=3.0
                )

            # Extract numpy audio
            audio_data = audio_values[0, 0].cpu().numpy()
            sr = self.loaded_model.config.audio_encoder.sampling_rate

            # Normalize and convert to int16
            audio_data = audio_data / (np.max(np.abs(audio_data)) + 1e-6)
            int16_audio = (audio_data * 32767).astype(np.int16)

            os.makedirs(TRACKS_DIR, exist_ok=True)
            out_file = os.path.join(TRACKS_DIR, f"{track_id}.wav")
            wav.write(out_file, sr, int16_audio)

            peaks = compute_waveform_peaks(audio_data, num_peaks=120)
            actual_dur = float(len(audio_data)) / float(sr)
            return out_file, peaks, round(actual_dur, 2)

        except Exception as e:
            logger.warning(f"PyTorch MusicGen generation failed ({e}), using studio neural synthesizer fallback.")
            return generate_music_track(
                track_id=track_id,
                title=prompt,
                genre=genre,
                bpm=bpm,
                duration_sec=duration_sec,
                seed=seed
            )

# Global singleton
musicgen_engine = MusicGenEngine()
