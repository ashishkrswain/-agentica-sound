import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import FRONTEND_DIR, TRACKS_DIR
from backend.api.routes_auth import router as auth_router
from backend.api.routes_music import router as music_router
from backend.api.routes_hardware import router as hardware_router
from backend.api.routes_models import router as models_router
from backend.api.routes_intelligence import router as intelligence_router
from backend.db.repository import track_repo, Track
from backend.core.audio_synth import generate_music_track

app = FastAPI(
    title="Agentica Sound — Suno AI Local Music Studio",
    description="Local Hardware AI Music Generation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth_router)
app.include_router(music_router)
app.include_router(hardware_router)
app.include_router(models_router)
app.include_router(intelligence_router)

# Mount static files
static_dir = FRONTEND_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/login.html")
def serve_login():
    return FileResponse(str(FRONTEND_DIR / "login.html"))

@app.get("/index.html")
def serve_dashboard():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.on_event("startup")
def startup_seed():
    os.makedirs(TRACKS_DIR, exist_ok=True)
    if track_repo.count() == 0:
        # Seed initial demo tracks so the user has immediate audio playback
        demos = [
            {
                "id": "demo-neon-synthwave-v1",
                "title": "Midnight Neon Highway [V1]",
                "prompt": "80s retro synthwave, analog synthesizers, neon night drive, arpeggiated bass",
                "genre": "Synthwave",
                "bpm": 124,
                "key": "A Minor",
                "duration": 20.0,
                "is_instrumental": True,
                "lyrics": "[Instrumental Track]\n(Atmospheric analog synth intro)\n(Driving arpeggiator)\n(Stereo chorus leads)",
                "variation_label": "v1"
            },
            {
                "id": "demo-lofi-coffee-v1",
                "title": "Rainy Cafe Coding [V1]",
                "prompt": "Cozy lofi hip hop, Rhodes electric piano, mellow vinyl dust, chill study beats",
                "genre": "Lo-Fi",
                "bpm": 80,
                "key": "C Major",
                "duration": 20.0,
                "is_instrumental": True,
                "lyrics": "[Instrumental Track]\n(Warm tape flutter)\n(Gentle jazzy chords)\n(Soft hip hop swing)",
                "variation_label": "v1"
            },
            {
                "id": "demo-cyberpunk-matrix-v1",
                "title": "Cyber City Overdrive [V1]",
                "prompt": "Dystopian cyberpunk electronic, industrial beat, distorted bassline, futuristic",
                "genre": "Cyberpunk",
                "bpm": 135,
                "key": "D Minor",
                "duration": 20.0,
                "is_instrumental": False,
                "lyrics": "[Intro]\n(Neural interface online)\n\n[Verse 1]\nWires in my veins, circuits in my head\nCounting down the seconds while the city bled\n\n[Chorus]\nBreak the protocol, sever the line\nThis revolution is yours and mine",
                "variation_label": "v1"
            }
        ]
        for d in demos:
            f_path, peaks, dur = generate_music_track(
                track_id=d["id"],
                title=d["title"],
                genre=d["genre"],
                bpm=d["bpm"],
                duration_sec=d["duration"],
                seed=4242
            )
            t = Track(
                id=d["id"],
                title=d["title"],
                prompt=d["prompt"],
                style_tags=f"{d['genre']}, {d['bpm']} BPM, {d['key']}",
                genre=d["genre"],
                bpm=d["bpm"],
                key=d["key"],
                duration=dur,
                is_instrumental=d["is_instrumental"],
                lyrics=d["lyrics"],
                engine_used="Local Neural-Synth (GTX 1650)",
                variation_label=d["variation_label"],
                file_path=f_path,
                audio_url=f"/api/music/audio/{d['id']}.wav",
                waveform_data=peaks,
                hardware_info="NVIDIA GeForce GTX 1650 (Local)"
            )
            track_repo.save(t)

if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
