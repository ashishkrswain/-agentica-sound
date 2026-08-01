from fastapi import APIRouter
import time
from backend.core.hardware_monitor import get_hardware_stats
from backend.core.musicgen_loader import musicgen_engine

router = APIRouter(prefix="/api/hardware", tags=["hardware"])

@router.get("/status")
def hardware_status():
    stats = get_hardware_stats()
    musicgen_info = musicgen_engine.get_status()
    return {
        "status": "online",
        "hardware": stats.to_dict(),
        "musicgen": musicgen_info,
        "timestamp": time.time()
    }

@router.get("/benchmark")
def run_benchmark():
    start = time.perf_counter()
    # Fast 5-second synth benchmark to estimate render speed
    from backend.core.audio_synth import synth_pad_chord
    synth_pad_chord([261.63, 329.63, 392.00], 5.0, 44100)
    elapsed = time.perf_counter() - start
    speed_factor = round(5.0 / max(0.001, elapsed), 1)

    return {
        "benchmark": "audio_dsp_5s",
        "elapsed_sec": round(elapsed, 4),
        "speed_multiplier": f"{speed_factor}x Realtime",
        "recommended_duration_max": 120
    }
