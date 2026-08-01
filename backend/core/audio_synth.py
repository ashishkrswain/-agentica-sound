import os
import math
import random
import numpy as np
import scipy.io.wavfile as wav
from typing import Tuple, List, Dict, Any
from pathlib import Path
from backend.config import SAMPLE_RATE, TRACKS_DIR

NOTE_FREQS = {
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00, "A3": 220.00, "B3": 246.94,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99, "A5": 880.00, "B5": 987.77,
    "A2": 110.00, "F2": 87.31, "G2": 98.00, "D2": 73.42, "E2": 82.41, "C2": 65.41
}

PROGRESSIONS = {
    "Synthwave": [
        ["A3", "C4", "E4"],  # Am
        ["F3", "A3", "C4"],  # F
        ["C3", "E3", "G3"],  # C
        ["G3", "B3", "D4"],  # G
    ],
    "Lo-Fi": [
        ["C4", "E4", "G4", "B4"],  # Cmaj7
        ["A3", "C4", "E4", "G4"],  # Am7
        ["D4", "F4", "A4", "C5"],  # Dm7
        ["G3", "B3", "D4", "F4"],  # G7
    ],
    "Cyberpunk": [
        ["D3", "F3", "A3"],  # Dm
        ["A#2", "D3", "F3"], # Bb
        ["C3", "E3", "G3"],  # C
        ["A2", "C#3", "E3"], # A
    ],
    "Cinematic Epic": [
        ["D3", "F3", "A3"],  # Dm
        ["A#2", "D3", "F3"], # Bb
        ["F3", "A3", "C4"],  # F
        ["C3", "E3", "G3"],  # C
    ],
    "Deep House": [
        ["F3", "G#3", "C4"], # Fm
        ["C#3", "F3", "G#3"],# Db
        ["A#2", "D3", "F3"], # Bbm
        ["C3", "E3", "G3"],  # C
    ],
    "Rock": [
        ["E3", "B3", "E4"],  # E5
        ["G3", "D4", "G4"],  # G5
        ["A3", "E4", "A4"],  # A5
        ["C3", "G3", "C4"],  # C5
    ]
}

def synth_kick(sr: int, duration_sec: float = 0.3) -> np.ndarray:
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    freq = 150.0 * np.exp(-t * 28.0) + 40.0
    phase = 2 * np.pi * np.cumsum(freq) / sr
    env = np.exp(-t * 14.0)
    kick = np.sin(phase) * env
    return np.clip(kick * 1.2, -1.0, 1.0)

def synth_snare(sr: int, duration_sec: float = 0.25) -> np.ndarray:
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    body = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 22.0)
    noise = (np.random.rand(n_samples) * 2 - 1) * np.exp(-t * 18.0)
    snare = body * 0.4 + noise * 0.6
    return np.clip(snare * 0.9, -1.0, 1.0)

def synth_hihat(sr: int, duration_sec: float = 0.08) -> np.ndarray:
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    noise = (np.random.rand(n_samples) * 2 - 1) * np.exp(-t * 45.0)
    return noise * 0.4

def synth_pad_chord(freqs: List[float], duration_sec: float, sr: int) -> Tuple[np.ndarray, np.ndarray]:
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    left = np.zeros(n_samples)
    right = np.zeros(n_samples)

    attack = int(sr * min(0.3, duration_sec * 0.2))
    release = int(sr * min(0.4, duration_sec * 0.2))
    env = np.ones(n_samples)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        env[-release:] = np.linspace(1, 0, release)

    for f in freqs:
        f_left = f * 0.997
        f_right = f * 1.003
        osc_l = 0.6 * np.sin(2 * np.pi * f_left * t) + 0.3 * np.sin(2 * np.pi * (2 * f_left) * t)
        osc_r = 0.6 * np.sin(2 * np.pi * f_right * t) + 0.3 * np.sin(2 * np.pi * (2 * f_right) * t)
        left += osc_l
        right += osc_r

    norm = len(freqs) or 1
    return (left / norm) * env * 0.4, (right / norm) * env * 0.4

def synth_bass_note(freq: float, duration_sec: float, sr: int, style: str) -> np.ndarray:
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    env = np.exp(-t * 4.0)

    if style in ["Synthwave", "Cyberpunk"]:
        # Sawtooth harmonic bass
        saw = 2 * (t * freq - np.floor(t * freq + 0.5))
        sub = np.sin(2 * np.pi * (freq * 0.5) * t)
        bass = (saw * 0.6 + sub * 0.5) * env
    else:
        # Deep rounded sub bass
        sub = np.sin(2 * np.pi * freq * t)
        harm = np.sin(2 * np.pi * (freq * 2) * t) * 0.25
        bass = (sub + harm) * env

    return np.clip(bass * 0.6, -1.0, 1.0)

def synth_lead_note(freq: float, duration_sec: float, sr: int) -> Tuple[np.ndarray, np.ndarray]:
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    vibrato = 1.0 + 0.015 * np.sin(2 * np.pi * 5.5 * t)
    phase = 2 * np.pi * freq * np.cumsum(vibrato) / sr
    osc = np.sin(phase) + 0.35 * np.sin(phase * 2) + 0.15 * np.sin(phase * 3)
    env = np.exp(-t * 2.5)
    signal = osc * env * 0.35
    # Slight stereo width
    return signal * 0.95, signal * 1.05

def generate_music_track(
    track_id: str,
    title: str,
    genre: str = "Synthwave",
    bpm: int = 120,
    duration_sec: float = 30.0,
    seed: int = None
) -> Tuple[str, List[float], float]:
    """
    Renders high-quality multi-track stereo WAV audio file,
    computes audio waveform peaks, and returns (file_path, waveform_peaks, actual_duration).
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    sr = SAMPLE_RATE
    total_samples = int(sr * duration_sec)
    left_master = np.zeros(total_samples, dtype=np.float32)
    right_master = np.zeros(total_samples, dtype=np.float32)

    beat_dur = 60.0 / max(40, bpm)
    beat_samples = int(sr * beat_dur)
    prog = PROGRESSIONS.get(genre, PROGRESSIONS["Synthwave"])

    # 1. Generate Drums Track
    kick = synth_kick(sr)
    snare = synth_snare(sr)
    hihat = synth_hihat(sr)

    total_beats = int(duration_sec / beat_dur)
    for b in range(total_beats):
        pos = b * beat_samples
        if pos >= total_samples:
            break

        # Kick on beats 1 and 3 (or 4-on-the-floor for House/Synthwave)
        is_kick = (b % 4 == 0) or (b % 4 == 2 and genre not in ["Rock", "Cinematic Epic"]) or (genre in ["Deep House", "Synthwave"] and b % 2 == 0)
        if is_kick:
            k_len = min(len(kick), total_samples - pos)
            left_master[pos:pos+k_len] += kick[:k_len] * 0.7
            right_master[pos:pos+k_len] += kick[:k_len] * 0.7

        # Snare on beats 2 and 4
        if b % 4 == 2 or (genre in ["Rock", "Cyberpunk", "Synthwave"] and (b % 4 == 1 or b % 4 == 3)):
            s_len = min(len(snare), total_samples - pos)
            left_master[pos:pos+s_len] += snare[:s_len] * 0.6
            right_master[pos:pos+s_len] += snare[:s_len] * 0.6

        # Hi-hat on 8th notes
        h_pos = pos + beat_samples // 2
        if h_pos < total_samples:
            h_len = min(len(hihat), total_samples - h_pos)
            left_master[h_pos:h_pos+h_len] += hihat[:h_len] * 0.35
            right_master[h_pos:h_pos+h_len] += hihat[:h_len] * 0.4

    # 2. Generate Harmony & Chords
    chord_beats = 4  # 1 chord per bar (4 beats)
    bar_samples = chord_beats * beat_samples

    for bar_idx in range(int(math.ceil(total_beats / chord_beats))):
        c_chord = prog[bar_idx % len(prog)]
        freqs = [NOTE_FREQS.get(n, 261.63) for n in c_chord]
        c_dur = chord_beats * beat_dur
        pad_l, pad_r = synth_pad_chord(freqs, c_dur, sr)

        pos = bar_idx * bar_samples
        p_len = min(len(pad_l), total_samples - pos)
        if p_len > 0 and pos < total_samples:
            left_master[pos:pos+p_len] += pad_l[:p_len]
            right_master[pos:pos+p_len] += pad_r[:p_len]

    # 3. Generate Bassline
    sixteenth_samples = max(1, beat_samples // 4)
    total_16ths = int(total_samples / sixteenth_samples)

    for s_idx in range(total_16ths):
        pos = s_idx * sixteenth_samples
        if pos >= total_samples:
            break
        # Match chord root
        bar_idx = (s_idx // 16) % len(prog)
        root_note = prog[bar_idx][0]
        base_freq = NOTE_FREQS.get(root_note, 130.81) / 2.0  # drop octave

        # Octave bounce for Synthwave/EDM or steady 8ths
        if genre in ["Synthwave", "Cyberpunk", "Deep House"]:
            oct_mult = 2.0 if (s_idx % 4 == 2) else 1.0
            b_freq = base_freq * oct_mult
            b_dur = sixteenth_samples / sr
            bass_hit = synth_bass_note(b_freq, b_dur, sr, genre)
            b_len = min(len(bass_hit), total_samples - pos)
            left_master[pos:pos+b_len] += bass_hit[:b_len] * 0.5
            right_master[pos:pos+b_len] += bass_hit[:b_len] * 0.5
        elif s_idx % 4 == 0:  # standard on-beat bass
            bass_hit = synth_bass_note(base_freq, beat_dur * 0.8, sr, genre)
            b_len = min(len(bass_hit), total_samples - pos)
            left_master[pos:pos+b_len] += bass_hit[:b_len] * 0.55
            right_master[pos:pos+b_len] += bass_hit[:b_len] * 0.55

    # 4. Generate Melodic Leads (Intro, Hook, Variations)
    lead_start_beat = 4  # lead kicks in after 1 bar intro
    scale_notes = [NOTE_FREQS.get(n, 440.0) for n in ["A4", "C5", "D5", "E5", "G5", "A5"]]
    curr_beat = lead_start_beat
    while curr_beat < total_beats - 2:
        note_freq = random.choice(scale_notes)
        dur_beats = random.choice([0.5, 1.0, 1.5, 2.0])
        l_dur = dur_beats * beat_dur
        pos = int(curr_beat * beat_samples)
        if pos < total_samples:
            lead_l, lead_r = synth_lead_note(note_freq, l_dur, sr)
            l_len = min(len(lead_l), total_samples - pos)
            left_master[pos:pos+l_len] += lead_l[:l_len] * 0.5
            right_master[pos:pos+l_len] += lead_r[:l_len] * 0.5

            # Simple stereo delay echo
            delay_samples = int(sr * 0.25)
            echo_pos = pos + delay_samples
            if echo_pos < total_samples:
                e_len = min(len(lead_l), total_samples - echo_pos)
                left_master[echo_pos:echo_pos+e_len] += lead_r[:e_len] * 0.2
                right_master[echo_pos:echo_pos+e_len] += lead_l[:e_len] * 0.2

        curr_beat += dur_beats

    # 5. Master Limit & Soft Clip
    stereo = np.column_stack((left_master, right_master))
    # Soft saturation curve: tanh
    stereo = np.tanh(stereo * 1.2)
    # Normalize to peak -0.5 dB
    max_val = np.max(np.abs(stereo))
    if max_val > 0:
        stereo = stereo / max_val * 0.94

    # 6. Save WAV file
    os.makedirs(TRACKS_DIR, exist_ok=True)
    filename = f"{track_id}.wav"
    file_path = os.path.join(TRACKS_DIR, filename)
    audio_int16 = (stereo * 32767).astype(np.int16)
    wav.write(file_path, sr, audio_int16)

    # 7. Compute 120 waveform peak points for UI canvas
    mono = np.mean(np.abs(stereo), axis=1)
    chunk_size = max(1, len(mono) // 120)
    waveform_peaks = []
    for i in range(120):
        chunk = mono[i * chunk_size : (i + 1) * chunk_size]
        peak = float(np.max(chunk)) if len(chunk) > 0 else 0.05
        waveform_peaks.append(round(min(1.0, max(0.08, peak)), 3))

    return file_path, waveform_peaks, duration_sec
