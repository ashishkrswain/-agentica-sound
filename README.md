# Agentica Sound — Suno AI Local Music Workstation

> A production-grade, local hardware AI music generation system inspired by **Suno AI** and architected using the **Agentica (`agentrc`)** specifications with a design system mirrored from **Copy Trader**.

---

## 🌟 Key Features

1. **Suno AI-Style Music Generation**:
   - **Dual Variations Generation**: Concurrently creates **Track [V1]** and **Track [V2]** for each prompt with distinct seeds and rhythmic variations, matching Suno AI's signature dual-generation workflow.
   - **Simple & Custom Modes**:
     - *Simple Mode*: Natural language prompt describing mood, genre, and instruments.
     - *Custom Mode*: Song title, style tags, and structured lyrics with section markers (`[Verse]`, `[Chorus]`, `[Bridge]`, `[Guitar Solo]`, `[Outro]`).
   - **AI Lyricist Lab**: Built-in intelligent lyric writer that crafts genre-aligned verses, choruses, and hooks with rhyming cadence.
   - **Interactive Waveform Player**: Real-time canvas rendering of audio amplitude peaks with seekable scrub-bar, loop, restart, and master playback.
   - **Persistent Floating Audio Dock**: Uninterrupted playback across all studio views with track art, seek slider, and volume control.

2. **Local Hardware Engine**:
   - **NVIDIA GPU Acceleration**: Live telemetry query for NVIDIA GeForce GTX 1650 (CUDA 12.8, VRAM monitoring, temperature, and utilization).
   - **Zero-Cloud Architecture**: Runs completely on local hardware without recurring subscription fees or cloud token burn.
   - **Hybrid Audio Synthesis**: Multi-track stereo 44.1kHz audio generator with drums, bass arpeggios, detuned supersaw chords, and melodic leads.
   - **PyTorch / Transformers MusicGen Integration**: Ready adapter for `facebook/musicgen-small` token generation.

3. **Copy-Trader Mirrored UI Design**:
   - **Side Split Login (`login.html`)**: Left-side brand panel with musical glyph mark, studio pitch, and hardware badges; right-side clean sign-in card with user ID, password toggle, and remember me checkbox.
   - **Workstation Layout (`index.html`)**:
     - **Left Sidebar**: Brand mark, studio navigation, live GPU status bar, and **User ID representation at the bottom left** (`ashish_local` / Studio Master profile with sign-out action).
     - **Center Main Content**: Live system clock, CUDA active badge, top metric stat cards, and the Creation Studio.
     - **Right Panel**: "What you have generated & Play options" with Spotlight Player card (interactive waveform, controls, WAV download, copy prompt, lyrics modal) and library playlist queue.

---

## 🚀 Quick Start

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

## 📂 Project Structure

```
agentica-music/
├── README.md
├── requirements.txt
├── start.bat
├── storage/
│   ├── tracks/                 # Generated WAV audio files
│   └── agentica_sound.db       # SQLite track database
├── backend/
│   ├── config.py               # Paths, ports, and defaults
│   ├── main.py                 # FastAPI application
│   ├── domain/
│   │   ├── song.py             # Track entity
│   │   ├── hardware.py         # Hardware stats model
│   │   └── user.py             # User profile model
│   ├── core/
│   │   ├── security.py         # Session token verification
│   │   ├── hardware_monitor.py # NVIDIA GPU & CPU profiler
│   │   ├── lyrics_ai.py        # Lyricist generator & style matcher
│   │   ├── audio_synth.py      # Multi-track stereo audio synthesizer
│   │   └── musicgen_loader.py  # PyTorch MusicGen adapter
│   ├── db/
│   │   └── repository.py       # SQLite database persistence
│   └── api/
│       ├── routes_auth.py      # Authentication endpoints
│       ├── routes_music.py     # Music generation & audio streaming
│       └── routes_hardware.py  # GPU & system diagnostics
└── frontend/
    ├── login.html              # Copy-Trader inspired split login
    ├── index.html              # 3-column studio dashboard
    └── static/
        ├── css/
        │   └── app.css         # Workstation CSS stylesheet
        └── js/
            ├── config.js       # Client configuration
            ├── api.js          # REST client with auth headers
            ├── player.js       # Waveform visualizer & audio engine
            └── app.js          # Studio controller & UI events
```
