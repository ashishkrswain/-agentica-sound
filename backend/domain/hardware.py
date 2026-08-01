from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class HardwareStats:
    gpu_name: str
    gpu_driver: str
    cuda_version: str
    vram_total_mb: int
    vram_used_mb: int
    vram_free_mb: int
    gpu_temp_c: int
    gpu_utilization_pct: int
    cpu_cores_physical: int
    cpu_cores_logical: int
    cpu_utilization_pct: float
    ram_total_gb: float
    ram_used_gb: float
    ram_free_gb: float
    ram_utilization_pct: float
    active_engine: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gpu_name": self.gpu_name,
            "gpu_driver": self.gpu_driver,
            "cuda_version": self.cuda_version,
            "vram_total_mb": self.vram_total_mb,
            "vram_used_mb": self.vram_used_mb,
            "vram_free_mb": self.vram_free_mb,
            "gpu_temp_c": self.gpu_temp_c,
            "gpu_utilization_pct": self.gpu_utilization_pct,
            "cpu_cores_physical": self.cpu_cores_physical,
            "cpu_cores_logical": self.cpu_cores_logical,
            "cpu_utilization_pct": self.cpu_utilization_pct,
            "ram_total_gb": self.ram_total_gb,
            "ram_used_gb": self.ram_used_gb,
            "ram_free_gb": self.ram_free_gb,
            "ram_utilization_pct": self.ram_utilization_pct,
            "active_engine": self.active_engine,
        }
