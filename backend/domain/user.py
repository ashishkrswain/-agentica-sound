from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class User:
    username: str
    display_name: str
    role: str = "Studio Master"
    hardware_plan: str = "NVIDIA GTX 1650 (Local GPU)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "hardware_plan": self.hardware_plan,
        }
