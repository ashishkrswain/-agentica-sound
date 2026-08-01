// Master Audio Player & Waveform Visualizer
class AudioEngine {
  constructor() {
    this.audio = new Audio();
    this.currentTrack = null;
    this.isPlaying = false;
    this.isLooping = false;
    this.volume = 0.85;
    this.audio.volume = this.volume;

    this.waveformCanvas = document.getElementById("waveform-canvas");
    this.waveformProgress = document.getElementById("waveform-progress");
    this.ctx = this.waveformCanvas ? this.waveformCanvas.getContext("2d") : null;

    this.setupListeners();
  }

  setupListeners() {
    this.audio.addEventListener("timeupdate", () => this.onTimeUpdate());
    this.audio.addEventListener("ended", () => this.onEnded());
    this.audio.addEventListener("play", () => this.setPlayState(true));
    this.audio.addEventListener("pause", () => this.setPlayState(false));

    // Waveform click seeking
    const box = document.getElementById("waveform-box");
    if (box) {
      box.addEventListener("click", (e) => {
        if (!this.currentTrack || !this.audio.duration) return;
        const rect = box.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const pct = Math.max(0, Math.min(1, clickX / rect.width));
        this.audio.currentTime = pct * this.audio.duration;
      });
    }

    // Dock slider seeking
    const dockSlider = document.getElementById("dock-slider");
    if (dockSlider) {
      dockSlider.addEventListener("input", (e) => {
        if (!this.currentTrack || !this.audio.duration) return;
        const pct = parseFloat(e.target.value) / 100;
        this.audio.currentTime = pct * this.audio.duration;
      });
    }

    // Volume controls
    const volSlider = document.getElementById("volume-slider");
    if (volSlider) {
      volSlider.addEventListener("input", (e) => {
        this.volume = parseFloat(e.target.value) / 100;
        this.audio.volume = this.volume;
      });
    }
  }

  loadTrack(track, autoPlay = true) {
    this.currentTrack = track;
    this.audio.src = track.audio_url;

    // Update Spotlight UI
    document.getElementById("spotlight-title").textContent = track.title;
    document.getElementById("spotlight-tags").textContent = `${track.genre} • ${track.bpm} BPM • ${track.duration.toFixed(0)}s`;
    document.getElementById("spotlight-var").textContent = (track.variation_label || "v1").toUpperCase();
    document.getElementById("time-total").textContent = this.formatTime(track.duration);
    document.getElementById("time-curr").textContent = "00:00";

    // Update Dock UI
    const dock = document.getElementById("audio-dock");
    if (dock) dock.style.display = "grid";
    document.getElementById("dock-title").textContent = track.title;
    document.getElementById("dock-tags").textContent = `${track.genre} • ${track.bpm} BPM • ${track.key}`;
    document.getElementById("dock-time-total").textContent = this.formatTime(track.duration);

    // Draw waveform
    this.drawWaveform(track.waveform_data || []);

    // Set download link
    const dlBtn = document.getElementById("btn-dl-wav");
    if (dlBtn) dlBtn.href = track.audio_url;
    const dockDl = document.getElementById("dock-dl");
    if (dockDl) dockDl.href = track.audio_url;

    // Highlight row in playlist
    document.querySelectorAll(".track-row").forEach(el => {
      el.classList.toggle("playing", el.dataset.id === track.id);
    });

    if (autoPlay) {
      this.play();
    }
  }

  play() {
    if (!this.currentTrack) return;
    this.audio.play().catch(e => console.log("Audio autoplay prevented:", e));
  }

  pause() {
    this.audio.pause();
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  restart() {
    this.audio.currentTime = 0;
    this.play();
  }

  toggleLoop() {
    this.isLooping = !this.isLooping;
    this.audio.loop = this.isLooping;
    const loopBtn = document.getElementById("btn-loop");
    if (loopBtn) loopBtn.style.color = this.isLooping ? "var(--accent)" : "inherit";
  }

  setPlayState(playing) {
    this.isPlaying = playing;
    const playSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
    const pauseSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
    const iconHtml = playing ? pauseSvg : playSvg;
    
    const playBtn = document.getElementById("btn-spotlight-play");
    if (playBtn) playBtn.innerHTML = iconHtml;

    const dockPlay = document.getElementById("dock-play");
    if (dockPlay) dockPlay.innerHTML = iconHtml;

    // Update active mini play button
    if (this.currentTrack) {
      document.querySelectorAll(`.track-row[data-id="${this.currentTrack.id}"] .play-mini`).forEach(b => {
        b.innerHTML = iconHtml;
      });
    }
  }

  onTimeUpdate() {
    if (!this.audio.duration) return;
    const curr = this.audio.currentTime;
    const dur = this.audio.duration;
    const pct = (curr / dur) * 100;

    // Update waveform progress overlay
    if (this.waveformProgress) {
      this.waveformProgress.style.width = `${pct}%`;
    }

    // Update counters
    const currStr = this.formatTime(curr);
    const currEl = document.getElementById("time-curr");
    if (currEl) currEl.textContent = currStr;

    const dockCurr = document.getElementById("dock-time-curr");
    if (dockCurr) dockCurr.textContent = currStr;

    const dockSlider = document.getElementById("dock-slider");
    if (dockSlider) dockSlider.value = pct;
  }

  onEnded() {
    this.setPlayState(false);
    if (!this.isLooping) {
      this.audio.currentTime = 0;
      if (this.waveformProgress) this.waveformProgress.style.width = "0%";
    }
  }

  drawWaveform(peaks) {
    if (!this.ctx || !this.waveformCanvas) return;
    const canvas = this.waveformCanvas;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * (window.devicePixelRatio || 1);
    canvas.height = rect.height * (window.devicePixelRatio || 1);
    const ctx = this.ctx;
    ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

    const w = rect.width;
    const h = rect.height;
    ctx.clearRect(0, 0, w, h);

    if (!peaks || peaks.length === 0) {
      // Generate placeholder bars
      peaks = Array.from({ length: 60 }, () => Math.random() * 0.7 + 0.2);
    }

    const barWidth = Math.max(2, (w / peaks.length) - 1.5);
    const centerY = h / 2;

    for (let i = 0; i < peaks.length; i++) {
      const val = peaks[i];
      const barH = Math.max(4, val * (h - 8));
      const x = i * (w / peaks.length);
      const y = centerY - barH / 2;

      // Gradient bar styling
      const grad = ctx.createLinearGradient(0, y, 0, y + barH);
      grad.addColorStop(0, "#7c4dff");
      grad.addColorStop(1, "#3949ab");

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(x, y, barWidth, barH, 2) : ctx.rect(x, y, barWidth, barH);
      ctx.fill();
    }
  }

  formatTime(sec) {
    if (!sec || isNaN(sec)) return "00:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
}

// Global player
window.player = null;
