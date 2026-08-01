// Main Studio Application Logic
document.addEventListener("DOMContentLoaded", async () => {
  // Initialize Audio Player
  window.player = new AudioEngine();

  // Initialize UI State
  let tracks = [];
  let currentGenre = "Synthwave";
  let isCustomMode = false;

  // Elements
  const viewTitle = document.getElementById("view-title");
  const navBtns = document.querySelectorAll(".nav-btn");
  const views = document.querySelectorAll(".view");
  const clockEl = document.getElementById("clock");

  // Live Clock
  function updateClock() {
    const now = new Date();
    clockEl.textContent = now.toLocaleTimeString("en-GB", { hour12: false }) + " UTC+5:30";
  }
  setInterval(updateClock, 1000);
  updateClock();

  // Sidebar Navigation Tabs
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetView = btn.dataset.view;
      navBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      views.forEach(v => {
        v.classList.toggle("active", v.id === `view-${targetView}`);
      });

      const titleMap = {
        studio: "Create Music Studio",
        library: "Track Library",
        lyrics: "AI Lyricist Lab",
        hardware: "Local Hardware & GPU Telemetry",
        models: "Model Management & Offline Storage",
        settings: "Audio & Engine Settings"
      };
      if (viewTitle) viewTitle.textContent = titleMap[targetView] || "Studio";
    });
  });

  // User Profile at lower left
  const user = getUser();
  if (user) {
    const nameEl = document.getElementById("holder-name");
    const roleEl = document.getElementById("holder-role");
    const avatarEl = document.getElementById("holder-avatar");
    if (nameEl) nameEl.textContent = user.display_name || user.username;
    if (roleEl) roleEl.textContent = user.hardware_plan || "Local GPU • Active";
    if (avatarEl) avatarEl.textContent = (user.display_name || user.username).substring(0, 2).toUpperCase();
  }

  // Logout button
  const logoutBtn = document.getElementById("btn-logout");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        await api("/api/auth/logout", { method: "POST" });
      } catch (e) {}
      clearSession();
      window.location.href = "login.html";
    });
  }

  // Hardware Telemetry Polling
  async function pollHardware() {
    try {
      const data = await api("/api/hardware/status");
      const hw = data.hardware;
      if (!hw) return;

      // Update sidebar GPU bar
      const sidebarGpu = document.getElementById("sidebar-gpu-name");
      const sidebarBar = document.getElementById("sidebar-vram-fill");
      if (sidebarGpu) sidebarGpu.textContent = hw.gpu_name;
      if (sidebarBar) {
        const vramPct = (hw.vram_used_mb / hw.vram_total_mb) * 100;
        sidebarBar.style.width = `${Math.max(5, vramPct)}%`;
      }

      // Update top metric cards
      const gpuCard = document.getElementById("card-gpu");
      const vramCard = document.getElementById("card-vram");
      const cpuCard = document.getElementById("card-cpu");
      const engineCard = document.getElementById("card-engine");

      if (gpuCard) gpuCard.textContent = `${hw.gpu_name.replace("NVIDIA GeForce ", "")}`;
      if (vramCard) vramCard.textContent = `${hw.vram_used_mb}MB / ${hw.vram_total_mb}MB (${hw.vram_free_mb}MB Free)`;
      if (cpuCard) cpuCard.textContent = `${hw.cpu_cores_logical} Cores • ${hw.cpu_utilization_pct.toFixed(0)}% Util`;
      if (engineCard) engineCard.textContent = "Neural-Synth + PyTorch";

      // Update hardware view if active
      const hwFullGpu = document.getElementById("hw-full-gpu");
      if (hwFullGpu) {
        hwFullGpu.innerHTML = `
          <strong>Device:</strong> ${hw.gpu_name}<br>
          <strong>Driver:</strong> ${hw.gpu_driver} | <strong>CUDA:</strong> ${hw.cuda_version}<br>
          <strong>VRAM:</strong> ${hw.vram_used_mb} MB used / ${hw.vram_total_mb} MB total (${hw.vram_free_mb} MB free)<br>
          <strong>Temperature:</strong> ${hw.gpu_temp_c}°C | <strong>GPU Util:</strong> ${hw.gpu_utilization_pct}%<br>
          <strong>System RAM:</strong> ${hw.ram_used_gb} GB used / ${hw.ram_total_gb} GB total (${hw.ram_pct}%)<br>
          <strong>CPU:</strong> ${hw.cpu_cores_physical} Physical / ${hw.cpu_cores_logical} Logical Cores (${hw.cpu_utilization_pct}%)
        `;
      }
    } catch (e) {
      console.log("Hardware polling failed:", e);
    }
  }

  setInterval(pollHardware, CONFIG.POLL_INTERVAL_MS);
  pollHardware();

  // Mode Switcher (Simple Prompt vs Custom Lyrics)
  const btnModeSimple = document.getElementById("mode-simple");
  const btnModeCustom = document.getElementById("mode-custom");
  const customSection = document.getElementById("custom-lyrics-section");

  if (btnModeSimple && btnModeCustom) {
    btnModeSimple.addEventListener("click", () => {
      isCustomMode = false;
      btnModeSimple.classList.add("active");
      btnModeCustom.classList.remove("active");
      if (customSection) customSection.style.display = "none";
    });

    btnModeCustom.addEventListener("click", () => {
      isCustomMode = true;
      btnModeCustom.classList.add("active");
      btnModeSimple.classList.remove("active");
      if (customSection) customSection.style.display = "block";
    });
  }

  // Genre Pills
  const genrePills = document.querySelectorAll(".genre-pills .pill");
  const bpmInput = document.getElementById("param-bpm");
  const keySelect = document.getElementById("param-key");
  const promptInput = document.getElementById("prompt-input");

  genrePills.forEach(pill => {
    pill.addEventListener("click", () => {
      genrePills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      currentGenre = pill.dataset.genre;

      // Suggest default BPM
      const bpmMap = {
        "Synthwave": 124,
        "Lo-Fi": 80,
        "Cyberpunk": 135,
        "Cinematic Epic": 100,
        "Deep House": 126,
        "Rock": 138,
        "Acoustic Pop": 110,
        "Ambient Dream": 70
      };
      if (bpmInput && bpmMap[currentGenre]) bpmInput.value = bpmMap[currentGenre];
    });
  });

  // Duration Custom Selector Toggle
  const durSelect = document.getElementById("param-dur");
  const customDurWrap = document.getElementById("custom-dur-wrap");
  const customDurInput = document.getElementById("param-custom-dur");

  if (durSelect && customDurWrap) {
    durSelect.addEventListener("change", () => {
      if (durSelect.value === "custom") {
        customDurWrap.style.display = "block";
        if (customDurInput) customDurInput.focus();
      } else {
        customDurWrap.style.display = "none";
      }
    });
  }

  // Tag helper buttons in lyrics editor
  const lyricsTextarea = document.getElementById("lyrics-input");
  document.querySelectorAll(".btn-tag").forEach(btn => {
    btn.addEventListener("click", () => {
      if (!lyricsTextarea) return;
      const tag = btn.dataset.tag;
      const start = lyricsTextarea.selectionStart;
      const end = lyricsTextarea.selectionEnd;
      const text = lyricsTextarea.value;
      lyricsTextarea.value = text.substring(0, start) + `\n${tag}\n` + text.substring(end);
      lyricsTextarea.focus();
    });
  });

  // AI Lyrics Generator Button
  const btnAiLyrics = document.getElementById("btn-ai-lyrics");
  if (btnAiLyrics) {
    btnAiLyrics.addEventListener("click", async () => {
      const prompt = promptInput.value.trim() || currentGenre;
      btnAiLyrics.disabled = true;
      btnAiLyrics.textContent = "Writing...";
      try {
        const res = await api("/api/music/lyrics/generate", {
          method: "POST",
          body: { prompt, genre: currentGenre }
        });
        if (lyricsTextarea) lyricsTextarea.value = res.lyrics;
        const titleInput = document.getElementById("title-input");
        if (titleInput && !titleInput.value) titleInput.value = res.title;
      } catch (e) {
        alert("Failed to generate lyrics: " + e.message);
      } finally {
        btnAiLyrics.disabled = false;
        btnAiLyrics.innerHTML = "Auto-Write Lyrics";
      }
    });
  }

  // Load Tracks Function
  async function loadTracks() {
    try {
      const res = await api("/api/music/tracks");
      tracks = res.tracks || [];

      // Update total counter
      const totalCard = document.getElementById("card-total");
      const rightCount = document.getElementById("right-track-count");
      if (totalCard) totalCard.textContent = tracks.length;
      if (rightCount) rightCount.textContent = `${tracks.length} Tracks`;

      renderTrackList(tracks);
      renderLibraryTable(tracks);

      // If player has no track, load the first one without autoplay
      if (!window.player.currentTrack && tracks.length > 0) {
        window.player.loadTrack(tracks[0], false);
      }
    } catch (e) {
      console.log("Failed to load tracks:", e);
    }
  }

  function renderTrackList(list) {
    const container = document.getElementById("track-list");
    if (!container) return;

    if (list.length === 0) {
      container.innerHTML = `<div style="color:var(--dim); font-size:12px; padding:10px; text-align:center;">No tracks yet. Create your first track above.</div>`;
      return;
    }

    const playSvg = '<svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
    const dlSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>';

    container.innerHTML = list.map(t => `
      <div class="track-row ${window.player.currentTrack && window.player.currentTrack.id === t.id ? 'playing' : ''}" data-id="${t.id}">
        <button class="play-mini" title="Play track">${playSvg}</button>
        <div class="info">
          <div class="t-title">${escapeHtml(t.title)}</div>
          <div class="t-meta">
            <span>${t.genre}</span> &bull; <span>${t.bpm} BPM</span> &bull; <span>${Math.round(t.duration)}s</span>
          </div>
        </div>
        <div class="t-actions">
          <a class="icon-btn" href="${t.audio_url}" download="${t.title}.wav" title="Download WAV">${dlSvg}</a>
          <button class="icon-btn btn-del" data-id="${t.id}" title="Delete">&times;</button>
        </div>
      </div>
    `).join("");

    // Add click listeners to rows
    container.querySelectorAll(".track-row").forEach(row => {
      const tId = row.dataset.id;
      const trackObj = tracks.find(t => t.id === tId);

      row.addEventListener("click", (e) => {
        if (e.target.closest(".t-actions")) return;
        if (trackObj) {
          if (window.player.currentTrack && window.player.currentTrack.id === tId) {
            window.player.togglePlay();
          } else {
            window.player.loadTrack(trackObj, true);
          }
        }
      });
    });

    // Delete buttons
    container.querySelectorAll(".btn-del").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const tId = btn.dataset.id;
        if (confirm("Delete this generated track?")) {
          await api(`/api/music/tracks/${tId}`, { method: "DELETE" });
          await loadTracks();
        }
      });
    });
  }

  function renderLibraryTable(list) {
    const tbody = document.getElementById("library-tbody");
    if (!tbody) return;

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--dim); padding:20px;">No tracks in library.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map((t, idx) => `
      <tr>
        <td style="font-family:var(--mono);">${idx + 1}</td>
        <td><strong>${escapeHtml(t.title)}</strong></td>
        <td><span class="pill" style="font-size:10.5px; padding:2px 8px;">${t.genre}</span></td>
        <td>${t.bpm}</td>
        <td>${t.key}</td>
        <td>${Math.round(t.duration)}s</td>
        <td>
          <button class="btn-round" style="width:26px; height:26px; font-size:11px; display:inline-grid;" onclick="playLibraryTrack('${t.id}')">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          </button>
          <a class="btn-action" style="display:inline-flex; width:auto; padding:3px 8px; font-size:11px;" href="${t.audio_url}" download>WAV</a>
        </td>
      </tr>
    `).join("");
  }

  window.playLibraryTrack = (trackId) => {
    const t = tracks.find(item => item.id === trackId);
    if (t) window.player.loadTrack(t, true);
  };

  // Generation Action
  const btnCreate = document.getElementById("btn-create");
  const progressBar = document.getElementById("gen-progress");
  const progressText = document.getElementById("gen-status-text");

  if (btnCreate) {
    btnCreate.addEventListener("click", async () => {
      const prompt = promptInput.value.trim();
      const titleInput = document.getElementById("title-input");
      const title = titleInput ? titleInput.value.trim() : "";

      if (!prompt && !title) {
        alert("Please enter a song description or prompt!");
        promptInput.focus();
        return;
      }

      let duration = 30.0;
      if (durSelect && durSelect.value === "custom") {
        duration = parseFloat(customDurInput ? customDurInput.value : 30) || 30.0;
      } else if (durSelect) {
        duration = parseFloat(durSelect.value) || 30.0;
      }
      duration = Math.max(5.0, Math.min(360.0, duration));

      const bpm = parseInt(bpmInput.value) || 120;
      const key = keySelect.value;
      const isInst = document.getElementById("chk-instrumental").checked;
      const lyrics = lyricsTextarea ? lyricsTextarea.value.trim() : "";
      const dualVars = document.getElementById("chk-variations").checked;
      const engine = document.getElementById("param-engine").value;

      btnCreate.disabled = true;
      if (progressBar) progressBar.classList.add("active");
      if (progressText) progressText.textContent = `Synthesizing ${duration.toFixed(0)}s audio on local hardware...`;

      try {
        const res = await api("/api/music/generate", {
          method: "POST",
          body: {
            prompt,
            title,
            genre: currentGenre,
            bpm,
            key,
            duration,
            is_instrumental: isInst,
            lyrics: lyrics || null,
            dual_variations: dualVars,
            engine
          }
        });

        if (progressText) progressText.textContent = "Audio generation complete!";
        await loadTracks();

        // Autoplay the first newly created variation
        if (res.tracks && res.tracks.length > 0) {
          window.player.loadTrack(res.tracks[0], true);
        }
      } catch (err) {
        alert("Generation error: " + err.message);
      } finally {
        btnCreate.disabled = false;
        if (progressBar) progressBar.classList.remove("active");
      }
    });
  }

  // Spotlight Player controls
  document.getElementById("btn-spotlight-play")?.addEventListener("click", () => window.player.togglePlay());
  document.getElementById("dock-play")?.addEventListener("click", () => window.player.togglePlay());
  document.getElementById("btn-restart")?.addEventListener("click", () => window.player.restart());
  document.getElementById("btn-loop")?.addEventListener("click", () => window.player.toggleLoop());

  // Copy Prompt
  document.getElementById("btn-copy-prompt")?.addEventListener("click", () => {
    if (window.player.currentTrack && window.player.currentTrack.prompt) {
      navigator.clipboard.writeText(window.player.currentTrack.prompt);
      alert("Prompt copied to clipboard!");
    }
  });

  // View Lyrics Modal
  const lyricsModal = document.getElementById("modal-lyrics");
  const modalText = document.getElementById("modal-lyrics-text");
  document.getElementById("btn-view-lyrics")?.addEventListener("click", () => {
    if (window.player.currentTrack) {
      modalText.textContent = window.player.currentTrack.lyrics || "No lyrics available for this instrumental track.";
      lyricsModal.classList.add("active");
    }
  });

  document.getElementById("modal-close")?.addEventListener("click", () => {
    lyricsModal.classList.remove("active");
  });

  // Model Manager Telemetry & Download
  const btnDownloadModel = document.getElementById("btn-download-model");
  const modelStatusText = document.getElementById("model-status-text");
  const badgeModelStatus = document.getElementById("badge-model-status");

  async function pollModelStatus() {
    try {
      const data = await api("/api/models/status");
      if (data.download_state && data.download_state.is_downloading) {
        if (btnDownloadModel) btnDownloadModel.disabled = true;
        if (modelStatusText) modelStatusText.textContent = data.download_state.status;
        if (badgeModelStatus) {
          badgeModelStatus.textContent = `Downloading ${data.download_state.progress}%`;
          badgeModelStatus.style.background = "#fff3e0";
          badgeModelStatus.style.color = "#e65100";
        }
      } else if (data.is_cached) {
        if (btnDownloadModel) {
          btnDownloadModel.disabled = false;
          btnDownloadModel.textContent = "Weights Verified";
        }
        if (modelStatusText) modelStatusText.textContent = "Local weights ready in storage/models";
        if (badgeModelStatus) {
          badgeModelStatus.textContent = "Cached & Ready";
          badgeModelStatus.style.background = "var(--accent-soft)";
          badgeModelStatus.style.color = "var(--accent)";
        }
      }
    } catch (e) {}
  }
  setInterval(pollModelStatus, 4000);
  pollModelStatus();

  if (btnDownloadModel) {
    btnDownloadModel.addEventListener("click", async () => {
      btnDownloadModel.disabled = true;
      btnDownloadModel.textContent = "Starting download...";
      try {
        await api("/api/models/download", { method: "POST" });
        pollModelStatus();
      } catch (err) {
        alert("Download error: " + err.message);
        btnDownloadModel.disabled = false;
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Load initial tracks
  await loadTracks();
});
