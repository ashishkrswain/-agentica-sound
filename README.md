# Agentica Sound — Suno AI Local Music Workstation

> A production-grade, local hardware AI music generation system inspired by **Suno AI** and architected using the **Agentica (`agentrc`)** specifications with a design system mirrored from **Copy Trader**.

---

## Key Features

1. **Suno AI-Style Music Generation**:
   - **Dual Variations Generation**: Concurrently creates **Track [V1]** and **Track [V2]** for each prompt with distinct seeds and rhythmic variations, matching Suno AI's signature dual-generation workflow.
   - **Simple & Custom Modes**:
     - *Simple Mode*: Natural language prompt describing mood, genre, and instruments.
     - *Custom Mode*: Song title, style tags, and structured lyrics with section markers (`[Verse]`, `[Chorus]`, `[Bridge]`, `[Guitar Solo]`, `[Outro]`).
   - **Custom Duration Input**: Specify custom duration from 5 to 360 seconds (up to 6 minutes).
   - **AI Lyricist Lab**: Built-in intelligent lyric writer that crafts genre-aligned verses, choruses, and hooks with rhyming cadence.
   - **Interactive Waveform Player**: Real-time canvas rendering of audio amplitude peaks with seekable scrub-bar, loop, restart, and master playback.
   - **Persistent Floating Audio Dock**: Uninterrupted playback across all studio views with track art, seek slider, and volume control.
   - **Clean Helvetica Typography**: Crisp typography using standard Helvetica Neue / Helvetica without emojis.

2. **Hardware Execution Architecture Modes (Frontend Toggled)**:
   - **Hybrid Offload (GPU + CPU + System RAM)**: Balances NVIDIA GTX 1650 (4GB VRAM) and 16GB System RAM to guarantee zero out-of-memory errors on large audio models.
   - **Dedicated GPU (FP16 CUDA VRAM Only)**: Maximizes CUDA compute directly on the GPU for smaller models with ultra-fast inference.
   - **CPU & System RAM (Zero VRAM)**: Pure 8-core multithreaded CPU computation, freeing 100% of GPU resources.
   - **High-Fi Neural Synthesizer (Instant DSP)**: Built-in 44.1kHz stereo DSP engine with drum machines, bass arpeggios, chords, and leads with zero download and 0MB VRAM overhead.

3. **AI Musical Director (Big Model Blueprint Composer)**:
   - **Cloud & Local LLM Integration**: Directly connects to:
     - **NVIDIA NIM API** (`integrate.api.nvidia.com/v1`): Nemotron 340B, Llama 3.1 70B/405B, DeepSeek, GLM 4.
     - **Ollama Local Engine** (`http://127.0.0.1:11434`): Directly connects to any local Ollama model.
     - **LM Studio Local Engine** (`http://127.0.0.1:1234/v1`): OpenAI-compatible local GGUF server.
     - **OpenAI-Compatible Custom Endpoints**: Any custom API key and URL.
     - **Offline Music Theorist**: Built-in offline rule-based theorist fallback.
   - **Automated Blueprint Composition**: Generates complete song blueprint (Title, Lyrics, Chords, BPM, Key, Tone, Style tags) with one click to offload local hardware.

4. **Direct Hugging Face Repository Linkage**:
   - **Seamless Codebase Storage**: Enter any Hugging Face repo ID (`facebook/musicgen-small`, `reach-vb/musicgen-song-generation`, etc.) to download directly into `storage/models/{repo_slug}`.
   - **Zero Configuration Binding**: Downloaded models auto-bind immediately to the audio generation pipeline without external folder hunting.
   - **Local Installed Models Manager**: View installed models, disk sizes, and activate any model for studio synthesis with one click.

5. **Copy-Trader Mirrored UI Design**:
   - **Side Split Login (`login.html`)**: Left-side brand panel with clean AS mark, studio pitch, and hardware badges; right-side clean sign-in card with user ID, password toggle, and remember me checkbox.
   - **Workstation Layout (`index.html`)**:
     - **Left Sidebar**: Brand mark, studio navigation, live GPU status bar, and **User ID representation at the bottom left** (`ashish_local` / Studio Master profile with sign-out action).
     - **Center Main Content**: Live system clock, CUDA active badge, top metric stat cards, and the Creation Studio.
     - **Right Panel**: "What you have generated & Play options" with Spotlight Player card (interactive waveform, controls, WAV download, copy prompt, lyrics modal) and library playlist queue.

---

## Quick Start

### 1. Launch the Server

Double-click `start.bat` or run from PowerShell:

```powershell
cd C:\git_boom\agentica-music
& "C:\Users\ashis\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Access the Application

- **Login Page**: [http://127.0.0.1:8000/login.html](http://127.0.0.1:8000/login.html)
  - Default User ID: `ashish_local` (or `admin` / `creator`)
  - Default Password: `sound2026`
- **Studio Dashboard**: [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Project Structure

```
agentica-music/
├── README.md
├── requirements.txt
├── start.bat
├── storage/
│   ├── tracks/                 # Generated WAV audio files
│   ├── models/                 # Cached offline model weights (Hugging Face)
│   └── agentica_sound.db       # SQLite track database
├── backend/
│   ├── config.py               # Paths, ports, hardware modes, and defaults
│   ├── main.py                 # FastAPI application & router mounting
│   ├── domain/
│   │   ├── song.py             # Track entity
│   │   ├── hardware.py         # Hardware stats model
│   │   └── user.py             # User profile model
│   ├── core/
│   │   ├── security.py         # Session token verification
│   │   ├── hardware_monitor.py # NVIDIA GPU & CPU profiler
│   │   ├── lyrics_ai.py        # Lyricist generator & style matcher
│   │   ├── llm_brain.py        # Musical Intelligence (NVIDIA NIM / Ollama / LM Studio)
│   │   ├── model_manager.py    # Local model manager & Hugging Face downloader
│   │   ├── audio_synth.py      # Multi-track stereo audio synthesizer
│   │   └── musicgen_loader.py  # PyTorch MusicGen adapter
│   ├── db/
│   │   └── repository.py       # SQLite database persistence
│   └── api/
│       ├── routes_auth.py      # Authentication endpoints
│       ├── routes_music.py     # Music generation & audio streaming
│       ├── routes_hardware.py  # GPU & system diagnostics
│       ├── routes_models.py    # Offline model management & downloads
│       └── routes_intelligence.py # LLM Musical Director & blueprint endpoints
└── frontend/
    ├── login.html              # Copy-Trader inspired split login
    ├── index.html              # 3-column studio dashboard
    └── static/
        ├── css/
        │   └── app.css         # Workstation Helvetica CSS stylesheet
        └── js/
            ├── config.js       # Client configuration
            ├── api.js          # REST client with auth headers
            ├── player.js       # Waveform visualizer & audio engine
            └── app.js          # Studio controller, hardware toggles & LLM director
```

