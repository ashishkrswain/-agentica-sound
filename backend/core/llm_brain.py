import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from backend.core.lyrics_ai import generate_lyrics_and_style

class MusicalIntelligence:
    """
    Connects to NVIDIA NIM, Ollama, LM Studio, or OpenAI-compatible APIs
    to generate complete musical blueprints (lyrics, chords, BPM, key, tone, instruments).
    Falls back gracefully to the built-in offline music theorist.
    """
    def __init__(self):
        # Default configuration
        self.provider = "offline"  # "nvidia", "ollama", "lm_studio", "openai", "offline"
        self.nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "")
        self.nvidia_model = "meta/llama-3.1-70b-instruct"
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.openai_base_url = "https://api.openai.com/v1"
        self.openai_model = "gpt-4o-mini"
        self.ollama_url = "http://127.0.0.1:11434"
        self.ollama_model = "llama3"
        self.lm_studio_url = "http://127.0.0.1:1234/v1"
        self.lm_studio_model = "local-model"

    def update_config(self, cfg: Dict[str, Any]):
        if "provider" in cfg:
            self.provider = cfg["provider"]
        if "nvidia_api_key" in cfg:
            self.nvidia_api_key = cfg["nvidia_api_key"].strip()
        if "nvidia_model" in cfg:
            self.nvidia_model = cfg["nvidia_model"].strip()
        if "openai_api_key" in cfg:
            self.openai_api_key = cfg["openai_api_key"].strip()
        if "openai_base_url" in cfg:
            self.openai_base_url = cfg["openai_base_url"].strip()
        if "openai_model" in cfg:
            self.openai_model = cfg["openai_model"].strip()
        if "ollama_url" in cfg:
            self.ollama_url = cfg["ollama_url"].strip().rstrip("/")
        if "ollama_model" in cfg:
            self.ollama_model = cfg["ollama_model"].strip()
        if "lm_studio_url" in cfg:
            self.lm_studio_url = cfg["lm_studio_url"].strip().rstrip("/")
        if "lm_studio_model" in cfg:
            self.lm_studio_model = cfg["lm_studio_model"].strip()

    def get_config(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "has_nvidia_key": bool(self.nvidia_api_key),
            "nvidia_model": self.nvidia_model,
            "has_openai_key": bool(self.openai_api_key),
            "openai_base_url": self.openai_base_url,
            "openai_model": self.openai_model,
            "ollama_url": self.ollama_url,
            "ollama_model": self.ollama_model,
            "lm_studio_url": self.lm_studio_url,
            "lm_studio_model": self.lm_studio_model,
        }

    def test_connection(self, provider: str) -> Dict[str, Any]:
        """Tests connectivity to the chosen provider."""
        if provider == "ollama":
            try:
                req = urllib.request.Request(f"{self.ollama_url}/api/tags", headers={"User-Agent": "AgenticaSound"})
                with urllib.request.urlopen(req, timeout=3) as res:
                    data = json.loads(res.read().decode())
                    models = [m.get("name") for m in data.get("models", [])]
                    return {"success": True, "provider": "ollama", "models": models}
            except Exception as e:
                return {"success": False, "provider": "ollama", "error": f"Ollama not reachable at {self.ollama_url}: {str(e)}"}

        elif provider == "lm_studio":
            try:
                req = urllib.request.Request(f"{self.lm_studio_url}/models", headers={"User-Agent": "AgenticaSound"})
                with urllib.request.urlopen(req, timeout=3) as res:
                    data = json.loads(res.read().decode())
                    models = [m.get("id") for m in data.get("data", [])]
                    return {"success": True, "provider": "lm_studio", "models": models}
            except Exception as e:
                return {"success": False, "provider": "lm_studio", "error": f"LM Studio not reachable at {self.lm_studio_url}: {str(e)}"}

        elif provider == "nvidia":
            if not self.nvidia_api_key:
                return {"success": False, "provider": "nvidia", "error": "NVIDIA API Key is missing. Enter your key from build.nvidia.com."}
            try:
                req = urllib.request.Request(
                    "https://integrate.api.nvidia.com/v1/models",
                    headers={"Authorization": f"Bearer {self.nvidia_api_key}", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=4) as res:
                    return {"success": True, "provider": "nvidia", "message": "NVIDIA NIM API key is valid and connected!"}
            except Exception as e:
                return {"success": False, "provider": "nvidia", "error": f"NVIDIA API Error: {str(e)}"}

        elif provider == "openai":
            if not self.openai_api_key:
                return {"success": False, "provider": "openai", "error": "OpenAI / Open-Source API Key is missing."}
            try:
                req = urllib.request.Request(
                    f"{self.openai_base_url}/models",
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=4) as res:
                    return {"success": True, "provider": "openai", "message": "OpenAI API connection verified!"}
            except Exception as e:
                return {"success": False, "provider": "openai", "error": f"OpenAI API Error: {str(e)}"}

        return {"success": True, "provider": "offline", "message": "Built-in offline music intelligence active."}

    def compose_blueprint(self, prompt: str, genre_hint: str = None) -> Dict[str, Any]:
        """
        Generates full song arrangement blueprint (title, lyrics, chords, bpm, key, tone).
        Uses external LLM (NVIDIA NIM / Ollama / LM Studio) if active, else offline theorist.
        """
        system_prompt = (
            "You are a master AI Music Producer & Lyricist for Suno AI workstations. "
            "Given a song concept or prompt, output a JSON object with this exact structure:\n"
            "{\n"
            '  "title": "Song Title",\n'
            '  "genre": "Genre (e.g. Synthwave, Lo-Fi, Cyberpunk, Cinematic, Deep House, Rock)",\n'
            '  "bpm": 124,\n'
            '  "key": "A Minor",\n'
            '  "chord_progression": ["Am", "F", "C", "G"],\n'
            '  "tone_and_mood": "Description of energy, instrumentation and sound design",\n'
            '  "style_tags": "Genre, BPM, Key, Instruments, Sound Style",\n'
            '  "lyrics": "[Intro]\\n...\\n[Verse 1]\\n...\\n[Chorus]\\n...\\n[Verse 2]\\n...\\n[Bridge]\\n...\\n[Outro]\\n..."\n'
            "}\n"
            "Respond ONLY with valid JSON, no markdown backticks."
        )

        user_content = f"Song Concept: {prompt}\nGenre Preference: {genre_hint or 'Auto-detect'}"

        # 1. Try Ollama
        if self.provider == "ollama":
            try:
                payload = json.dumps({
                    "model": self.ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "stream": False,
                    "format": "json"
                }).encode("utf-8")
                req = urllib.request.Request(f"{self.ollama_url}/api/chat", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=12) as res:
                    data = json.loads(res.read().decode())
                    content = data.get("message", {}).get("content", "")
                    return json.loads(content)
            except Exception:
                pass

        # 2. Try LM Studio
        if self.provider == "lm_studio":
            try:
                payload = json.dumps({
                    "model": self.lm_studio_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.7
                }).encode("utf-8")
                req = urllib.request.Request(f"{self.lm_studio_url}/chat/completions", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=12) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_json(content)
            except Exception:
                pass

        # 3. Try NVIDIA NIM
        if self.provider == "nvidia" and self.nvidia_api_key:
            try:
                payload = json.dumps({
                    "model": self.nvidia_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.6,
                    "max_tokens": 1024
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {self.nvidia_api_key}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_json(content)
            except Exception:
                pass

        # 4. Try OpenAI Compatible
        if self.provider == "openai" and self.openai_api_key:
            try:
                payload = json.dumps({
                    "model": self.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.7
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.openai_base_url}/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=12) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_json(content)
            except Exception:
                pass

        # 5. Default / Fallback: Built-in Offline Music Theorist
        base = generate_lyrics_and_style(prompt, genre_hint)
        return {
            "title": base["title"],
            "genre": base["genre"],
            "bpm": base["bpm"],
            "key": base["key"],
            "chord_progression": ["Am", "F", "C", "G"] if "Minor" in base["key"] else ["C", "G", "Am", "F"],
            "tone_and_mood": f"Rich studio stereo arrangement, dynamic balance, mastered for local playback.",
            "style_tags": base["style_tags"],
            "lyrics": base["lyrics"],
            "provider_used": "Offline Music Theorist"
        }

    def _parse_json(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

# Global singleton
musical_intelligence = MusicalIntelligence()
