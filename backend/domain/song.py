from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class Track:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Track"
    prompt: str = ""
    style_tags: str = "Synthwave, 120 BPM"
    genre: str = "Synthwave"
    bpm: int = 120
    key: str = "C Major"
    duration: float = 30.0
    is_instrumental: bool = True
    lyrics: Optional[str] = None
    engine_used: str = "Local Neural-Synth"
    variation_label: str = "v1"
    file_path: str = ""
    audio_url: str = ""
    waveform_data: List[float] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_favorite: bool = False
    hardware_info: str = "NVIDIA GTX 1650 (Local)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "prompt": self.prompt,
            "style_tags": self.style_tags,
            "genre": self.genre,
            "bpm": self.bpm,
            "key": self.key,
            "duration": self.duration,
            "is_instrumental": self.is_instrumental,
            "lyrics": self.lyrics,
            "engine_used": self.engine_used,
            "variation_label": self.variation_label,
            "audio_url": self.audio_url,
            "waveform_data": self.waveform_data,
            "created_at": self.created_at,
            "is_favorite": self.is_favorite,
            "hardware_info": self.hardware_info,
        }
