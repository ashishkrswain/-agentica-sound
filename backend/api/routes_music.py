import os
import uuid
import random
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.domain.song import Track
from backend.db.repository import track_repo
from backend.core.audio_synth import generate_music_track
from backend.core.lyrics_ai import generate_lyrics_and_style
from backend.core.hardware_monitor import get_hardware_stats
from backend.config import TRACKS_DIR

router = APIRouter(prefix="/api/music", tags=["music"])

class MusicGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt describing the song or mood")
    title: Optional[str] = None
    genre: Optional[str] = "Synthwave"
    style_tags: Optional[str] = None
    lyrics: Optional[str] = None
    is_instrumental: bool = False
    duration: float = Field(30.0, ge=5.0, le=360.0)
    bpm: int = Field(120, ge=50, le=200)
    key: str = "C Major"
    engine: str = "Local Neural-Synth"
    dual_variations: bool = True  # Suno AI creates 2 variations per prompt

class LyricsGenerateRequest(BaseModel):
    prompt: str
    genre: Optional[str] = None

@router.post("/lyrics/generate")
def api_generate_lyrics(req: LyricsGenerateRequest):
    data = generate_lyrics_and_style(req.prompt, req.genre)
    return {
        "success": True,
        "title": data["title"],
        "genre": data["genre"],
        "bpm": data["bpm"],
        "key": data["key"],
        "lyrics": data["lyrics"],
        "style_tags": data["style_tags"]
    }

@router.post("/generate")
def api_generate_music(req: MusicGenerateRequest):
    if not req.prompt.strip() and not req.title:
        raise HTTPException(status_code=400, detail="Please enter a song prompt or title")

    # If lyrics are not provided and not instrumental, generate lyrics
    title = req.title.strip() if req.title and req.title.strip() else req.prompt.strip().title()[:40]
    genre = req.genre or "Synthwave"
    bpm = req.bpm or 120
    key = req.key or "C Major"
    style_tags = req.style_tags or f"{genre}, {bpm} BPM, {key}"
    lyrics = req.lyrics

    if not req.is_instrumental and not lyrics:
        auto_data = generate_lyrics_and_style(req.prompt, genre)
        lyrics = auto_data["lyrics"]

    hw = get_hardware_stats()
    hw_info = f"{hw.gpu_name} (Local {hw.cuda_version})"

    variations_to_generate = ["v1", "v2"] if req.dual_variations else ["v1"]
    generated_tracks = []

    for idx, var_label in enumerate(variations_to_generate):
        track_id = str(uuid.uuid4())
        var_seed = random.randint(1000, 999999) + idx * 42
        
        # Slight variation in tempo/melody for second variation like Suno
        var_bpm = bpm if idx == 0 else int(bpm * random.choice([0.98, 1.02, 1.0]))

        file_path, waveform_peaks, actual_duration = generate_music_track(
            track_id=track_id,
            title=title,
            genre=genre,
            bpm=var_bpm,
            duration_sec=req.duration,
            seed=var_seed
        )

        audio_url = f"/api/music/audio/{track_id}.wav"
        track_title = f"{title} [{var_label.upper()}]" if req.dual_variations else title

        track = Track(
            id=track_id,
            title=track_title,
            prompt=req.prompt,
            style_tags=style_tags,
            genre=genre,
            bpm=var_bpm,
            key=key,
            duration=actual_duration,
            is_instrumental=req.is_instrumental,
            lyrics=lyrics if not req.is_instrumental else "[Instrumental Track]",
            engine_used=req.engine,
            variation_label=var_label,
            file_path=file_path,
            audio_url=audio_url,
            waveform_data=waveform_peaks,
            hardware_info=hw_info
        )

        track_repo.save(track)
        generated_tracks.append(track.to_dict())

    return {
        "success": True,
        "count": len(generated_tracks),
        "tracks": generated_tracks
    }

@router.get("/tracks")
def api_list_tracks(limit: int = 50):
    tracks = track_repo.list_all(limit=limit)
    return {
        "count": len(tracks),
        "total": track_repo.count(),
        "tracks": [t.to_dict() for t in tracks]
    }

@router.get("/tracks/{track_id}")
def api_get_track(track_id: str):
    track = track_repo.get_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track.to_dict()

@router.get("/audio/{track_id}.wav")
def api_stream_audio(track_id: str):
    track = track_repo.get_by_id(track_id)
    if not track or not os.path.exists(track.file_path):
        # Check direct path in storage
        direct_path = os.path.join(TRACKS_DIR, f"{track_id}.wav")
        if os.path.exists(direct_path):
            return FileResponse(direct_path, media_type="audio/wav", filename=f"{track_id}.wav")
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        track.file_path,
        media_type="audio/wav",
        filename=f"{track.title.replace(' ', '_')}.wav"
    )

@router.delete("/tracks/{track_id}")
def api_delete_track(track_id: str):
    track = track_repo.get_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    if os.path.exists(track.file_path):
        try:
            os.remove(track.file_path)
        except Exception:
            pass

    deleted = track_repo.delete(track_id)
    return {"success": deleted, "track_id": track_id}

@router.post("/tracks/{track_id}/favorite")
def api_toggle_favorite(track_id: str):
    new_status = track_repo.toggle_favorite(track_id)
    if new_status is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return {"success": True, "track_id": track_id, "is_favorite": new_status}
