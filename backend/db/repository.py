import sqlite3
import json
from typing import List, Optional, Dict, Any
from backend.config import DB_PATH
from backend.domain.song import Track

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                title TEXT,
                prompt TEXT,
                style_tags TEXT,
                genre TEXT,
                bpm INTEGER,
                key TEXT,
                duration REAL,
                is_instrumental INTEGER,
                lyrics TEXT,
                engine_used TEXT,
                variation_label TEXT,
                file_path TEXT,
                audio_url TEXT,
                waveform_json TEXT,
                created_at TEXT,
                is_favorite INTEGER,
                hardware_info TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                display_name TEXT,
                password_hash TEXT,
                role TEXT,
                hardware_plan TEXT
            )
        """)
        conn.commit()

class TrackRepository:
    def __init__(self):
        init_db()

    def save(self, track: Track) -> None:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO tracks (
                    id, title, prompt, style_tags, genre, bpm, key, duration,
                    is_instrumental, lyrics, engine_used, variation_label,
                    file_path, audio_url, waveform_json, created_at, is_favorite, hardware_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track.id,
                track.title,
                track.prompt,
                track.style_tags,
                track.genre,
                track.bpm,
                track.key,
                track.duration,
                1 if track.is_instrumental else 0,
                track.lyrics or "",
                track.engine_used,
                track.variation_label,
                track.file_path,
                track.audio_url,
                json.dumps(track.waveform_data),
                track.created_at,
                1 if track.is_favorite else 0,
                track.hardware_info
            ))
            conn.commit()

    def get_by_id(self, track_id: str) -> Optional[Track]:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tracks WHERE id = ?", (track_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_track(row)

    def list_all(self, limit: int = 50) -> List[Track]:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tracks ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_track(r) for r in rows]

    def delete(self, track_id: str) -> bool:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_favorite(self, track_id: str) -> Optional[bool]:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_favorite FROM tracks WHERE id = ?", (track_id,))
            row = cursor.fetchone()
            if not row:
                return None
            new_fav = 0 if row[0] == 1 else 1
            cursor.execute("UPDATE tracks SET is_favorite = ? WHERE id = ?", (new_fav, track_id))
            conn.commit()
            return new_fav == 1

    def count(self) -> int:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tracks")
            return cursor.fetchone()[0]

    def _row_to_track(self, r: sqlite3.Row) -> Track:
        waveform = []
        try:
            if r["waveform_json"]:
                waveform = json.loads(r["waveform_json"])
        except Exception:
            waveform = []

        return Track(
            id=r["id"],
            title=r["title"],
            prompt=r["prompt"],
            style_tags=r["style_tags"],
            genre=r["genre"],
            bpm=r["bpm"],
            key=r["key"],
            duration=r["duration"],
            is_instrumental=bool(r["is_instrumental"]),
            lyrics=r["lyrics"],
            engine_used=r["engine_used"],
            variation_label=r["variation_label"],
            file_path=r["file_path"],
            audio_url=r["audio_url"],
            waveform_data=waveform,
            created_at=r["created_at"],
            is_favorite=bool(r["is_favorite"]),
            hardware_info=r["hardware_info"]
        )

# Global singleton
track_repo = TrackRepository()
