import subprocess
import psutil
from typing import Dict, Any
from backend.domain.hardware import HardwareStats

def get_hardware_stats() -> HardwareStats:
    # Defaults
    gpu_name = "NVIDIA GeForce GTX 1650"
    gpu_driver = "572.70"
    cuda_version = "12.8"
    vram_total_mb = 4096
    vram_used_mb = 320
    vram_free_mb = 3776
    gpu_temp_c = 46
    gpu_utilization_pct = 0
    active_engine = "Local Neural-Synth (44.1kHz Pro) + PyTorch MusicGen"

    # Try querying nvidia-smi
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu",
            "--format=csv,noheader,nounits"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
        if res.returncode == 0 and res.stdout.strip():
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            if len(parts) >= 7:
                gpu_name = parts[0]
                gpu_driver = parts[1]
                vram_total_mb = int(parts[2])
                vram_used_mb = int(parts[3])
                vram_free_mb = int(parts[4])
                gpu_temp_c = int(parts[5])
                gpu_utilization_pct = int(parts[6])
    except Exception:
        pass

    # CPU & RAM stats via psutil
    cpu_cores_p = psutil.cpu_count(logical=False) or 4
    cpu_cores_l = psutil.cpu_count(logical=True) or 8
    cpu_pct = psutil.cpu_percent(interval=None)

    mem = psutil.virtual_memory()
    ram_total_gb = round(mem.total / (1024**3), 2)
    ram_used_gb = round(mem.used / (1024**3), 2)
    ram_free_gb = round(mem.available / (1024**3), 2)
    ram_pct = mem.percent

    return HardwareStats(
        gpu_name=gpu_name,
        gpu_driver=gpu_driver,
        cuda_version=cuda_version,
        vram_total_mb=vram_total_mb,
        vram_used_mb=vram_used_mb,
        vram_free_mb=vram_free_mb,
        gpu_temp_c=gpu_temp_c,
        gpu_utilization_pct=gpu_utilization_pct,
        cpu_cores_physical=cpu_cores_p,
        cpu_cores_logical=cpu_cores_l,
        cpu_utilization_pct=cpu_pct,
        ram_total_gb=ram_total_gb,
        ram_used_gb=ram_used_gb,
        ram_free_gb=ram_free_gb,
        ram_utilization_pct=ram_pct,
        active_engine=active_engine,
    )
