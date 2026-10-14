import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from backend.core.lyrics_ai import generate_lyrics_and_style
from backend.config import DEFAULT_OLLAMA_URL, DEFAULT_LM_STUDIO_URL, DEFAULT_NVIDIA_URL, DEFAULT_GROK_URL, DEFAULT_OPENAI_URL

class MusicalIntelligence:
    """
    Connects to NVIDIA NIM, xAI/Grok, OpenAI, Ollama, or LM Studio APIs
    to generate complete musical blueprints and provide interactive music producer feedback.
    Falls back gracefully to the built-in offline music theorist.
    """
    def __init__(self):
        # Default configuration
        self.provider = "offline"  # "nvidia", "grok", "openai", "ollama", "lm_studio", "offline"
        
        # NVIDIA NIM
        self.nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "")
        self.nvidia_base_url = DEFAULT_NVIDIA_URL
        self.nvidia_model = "meta/llama-3.1-70b-instruct"
        
        # xAI / Grok
        self.grok_api_key = os.environ.get("GROK_API_KEY", "")
        self.grok_base_url = DEFAULT_GROK_URL
        self.grok_model = "grok-beta"
        
        # OpenAI & OpenAI-Compatible
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.openai_base_url = DEFAULT_OPENAI_URL
        self.openai_model = "gpt-4o-mini"
        
        # Local Ollama
        self.ollama_url = DEFAULT_OLLAMA_URL
        self.ollama_model = "llama3"
        
        # Local LM Studio
        self.lm_studio_url = DEFAULT_LM_STUDIO_URL
        self.lm_studio_model = "local-model"

    def update_config(self, cfg: Dict[str, Any]):
        if "provider" in cfg:
            self.provider = cfg["provider"]
        if "nvidia_api_key" in cfg:
            self.nvidia_api_key = cfg["nvidia_api_key"].strip()
        if "nvidia_model" in cfg:
            self.nvidia_model = cfg["nvidia_model"].strip()
        if "nvidia_base_url" in cfg:
            self.nvidia_base_url = cfg["nvidia_base_url"].strip().rstrip("/")
        if "grok_api_key" in cfg:
            self.grok_api_key = cfg["grok_api_key"].strip()
        if "grok_model" in cfg:
            self.grok_model = cfg["grok_model"].strip()
        if "grok_base_url" in cfg:
            self.grok_base_url = cfg["grok_base_url"].strip().rstrip("/")
        if "openai_api_key" in cfg:
            self.openai_api_key = cfg["openai_api_key"].strip()
        if "openai_base_url" in cfg:
            self.openai_base_url = cfg["openai_base_url"].strip().rstrip("/")
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
            "nvidia_base_url": self.nvidia_base_url,
            "has_grok_key": bool(self.grok_api_key),
            "grok_model": self.grok_model,
            "grok_base_url": self.grok_base_url,
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
                    f"{self.nvidia_base_url}/models",
                    headers={"Authorization": f"Bearer {self.nvidia_api_key}", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=4) as res:
                    return {"success": True, "provider": "nvidia", "message": "NVIDIA NIM API key is valid and connected!"}
            except Exception as e:
                return {"success": False, "provider": "nvidia", "error": f"NVIDIA API Error: {str(e)}"}

        elif provider == "grok":
            if not self.grok_api_key:
                return {"success": False, "provider": "grok", "error": "xAI Grok API Key is missing. Enter your key from console.x.ai."}
            try:
                req = urllib.request.Request(
                    f"{self.grok_base_url}/models",
                    headers={"Authorization": f"Bearer {self.grok_api_key}", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=5) as res:
                    return {"success": True, "provider": "grok", "message": "xAI Grok API connected successfully!"}
            except Exception as e:
                return {"success": False, "provider": "grok", "error": f"xAI Grok API Error: {str(e)}"}

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
        return self._query_llm(system_prompt, user_content, prompt, genre_hint)

    def consult_and_generate(self, prompt: str, genre_hint: str = None, consultation_notes: str = None) -> Dict[str, Any]:
        """
        Interactive consultation with the AI Music Director:
        Returns in-depth producer feedback, musical guidance, structure tips, and complete structured lyrics.
        """
        system_prompt = (
            "You are a legendary AI Music Executive Producer and Songwriter. "
            "The user will describe their musical vision, genre, vibe, and any specific questions. "
            "You must provide structured creative feedback on how the song should be crafted (arrangements, tone, chords, rhythm), "
            "and write complete, emotive, high-impact lyrics with section headers ([Intro], [Verse 1], [Chorus], [Verse 2], [Guitar Solo], [Bridge], [Chorus], [Outro]).\n"
            "Respond ONLY with a JSON object with this exact structure:\n"
            "{\n"
            '  "title": "Catchy Song Title",\n'
            '  "genre": "Precise Genre Name",\n'
            '  "bpm": 120,\n'
            '  "key": "C Major",\n'
            '  "chord_progression": ["Am", "F", "C", "G"],\n'
            '  "producer_feedback": "Detailed creative feedback: explain what synthesizers/guitars/drums to use, how the song dynamics build, vocal performance tips, and chord mood.",\n'
            '  "tone_and_mood": "Energy and emotional mood description",\n'
            '  "style_tags": "Genre, BPM, Key, Instrumentation tags",\n'
            '  "lyrics": "[Intro]\\n...\\n[Verse 1]\\n...\\n[Chorus]\\n...\\n[Verse 2]\\n...\\n[Bridge]\\n...\\n[Outro]\\n..."\n'
            "}\n"
            "Respond ONLY with valid JSON, no markdown backticks."
        )

        user_content = (
            f"Concept / Music Vision: {prompt}\n"
            f"Genre Hint: {genre_hint or 'Auto-detect'}\n"
            f"Consultation Questions / Creative Notes: {consultation_notes or 'Give me best recommendations for this track.'}"
        )
        return self._query_llm(system_prompt, user_content, prompt, genre_hint, is_consultation=True)

    def _query_llm(self, system_prompt: str, user_content: str, prompt: str, genre_hint: str = None, is_consultation: bool = False) -> Dict[str, Any]:
        """Dispatches LLM query to the active provider with automatic fallback."""
        
        # 1. Try xAI / Grok
        if self.provider == "grok" and self.grok_api_key:
            try:
                payload = json.dumps({
                    "model": self.grok_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.grok_base_url}/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {self.grok_api_key}", "Content-Type": "application/json", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=18) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._parse_json(content)
                    parsed["provider_used"] = f"xAI Grok ({self.grok_model})"
                    return parsed
            except Exception as e:
                print(f"Grok API call failed: {e}")

        # 2. Try NVIDIA NIM
        if self.provider == "nvidia" and self.nvidia_api_key:
            try:
                payload = json.dumps({
                    "model": self.nvidia_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.6,
                    "max_tokens": 1500
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.nvidia_base_url}/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {self.nvidia_api_key}", "Content-Type": "application/json", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=18) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._parse_json(content)
                    parsed["provider_used"] = f"NVIDIA NIM ({self.nvidia_model})"
                    return parsed
            except Exception as e:
                print(f"NVIDIA API call failed: {e}")

        # 3. Try OpenAI
        if self.provider == "openai" and self.openai_api_key:
            try:
                payload = json.dumps({
                    "model": self.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.openai_base_url}/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json", "User-Agent": "AgenticaSound"}
                )
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._parse_json(content)
                    parsed["provider_used"] = f"OpenAI ({self.openai_model})"
                    return parsed
            except Exception as e:
                print(f"OpenAI call failed: {e}")

        # 4. Try Ollama
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
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    content = data.get("message", {}).get("content", "")
                    parsed = json.loads(content)
                    parsed["provider_used"] = f"Ollama Local ({self.ollama_model})"
                    return parsed
            except Exception as e:
                print(f"Ollama call failed: {e}")

        # 5. Try LM Studio
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
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._parse_json(content)
                    parsed["provider_used"] = f"LM Studio ({self.lm_studio_model})"
                    return parsed
            except Exception as e:
                print(f"LM Studio call failed: {e}")

        # 6. Built-in Offline Music Theorist Fallback
        base = generate_lyrics_and_style(prompt, genre_hint)
        key = base["key"]
        progression = ["Am", "F", "C", "G"] if "Minor" in key else ["C", "G", "Am", "F"]
        
        feedback = (
            f"Producer Recommendations for '{base['title']}':\n"
            f"- Arrangement: Build from a filtered intro into punchy drums at bar 8. Layer warm analogue pad chords ({'-'.join(progression)}) with bright stereo arpeggios.\n"
            f"- Harmonic Foundation: Key of {key} provides emotional resonance. Keep bass tight in mono to prevent phase cancellation.\n"
            f"- Vocal Cadence: Verse sections should breathe with syncopated phrasing; deliver the chorus with wide doubled vocal presence."
        )

        return {
            "title": base["title"],
            "genre": base["genre"],
            "bpm": base["bpm"],
            "key": key,
            "chord_progression": progression,
            "producer_feedback": feedback,
            "tone_and_mood": "Dynamic balance, rich harmonic layering, mastered for local hardware synthesis.",
            "style_tags": base["style_tags"],
            "lyrics": base["lyrics"],
            "provider_used": "Built-in Offline Music Theorist"
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
