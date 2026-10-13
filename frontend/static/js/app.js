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

  // ------------------------------------------ Hardware Execution Mode Toggles ---
  const hwPills = document.querySelectorAll(".hw-mode-pill");
  const activeHwBadge = document.getElementById("active-hw-badge");
  const hwModeNote = document.getElementById("hw-mode-note");

  const hwModeDescriptions = {
    hybrid: "Hybrid Mode: Balances GTX 1650 (4GB VRAM) and 16GB System RAM to guarantee zero out-of-memory errors on large audio models.",
    gpu_only: "Dedicated GPU Mode: Accelerates synthesis directly on CUDA cores within GTX 1650 4GB FP16 VRAM envelope.",
    cpu_only: "CPU & RAM Mode: Uses 8-core multithreaded CPU computation, freeing 100% of GPU for other workstation tasks.",
    neural_synth: "Neural Synthesizer Mode: Built-in instant 44.1kHz DSP engine with zero VRAM overhead and zero latency."
  };

  const hwModeBadgeLabels = {
    hybrid: "Hybrid Offload Active",
    gpu_only: "Dedicated GPU Active",
    cpu_only: "CPU & RAM Active",
    neural_synth: "Neural Synth Active"
  };

  hwPills.forEach(pill => {
    pill.addEventListener("click", async () => {
      const mode = pill.dataset.mode;
      hwPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");

      if (activeHwBadge) activeHwBadge.textContent = hwModeBadgeLabels[mode] || mode;
      if (hwModeNote && hwModeDescriptions[mode]) {
        hwModeNote.querySelector("span").textContent = hwModeDescriptions[mode];
      }

      const engineCard = document.getElementById("card-engine");
      if (engineCard) {
        const engineCardMap = {
          hybrid: "Hybrid Offload (GPU+RAM)",
          gpu_only: "Dedicated CUDA GPU",
          cpu_only: "Multithreaded CPU",
          neural_synth: "High-Fi Neural Synth"
        };
        engineCard.textContent = engineCardMap[mode] || mode;
      }

      try {
        await api("/api/models/hardware-mode", {
          method: "POST",
          body: { mode }
        });
      } catch (err) {
        console.error("Failed to switch hardware mode:", err);
      }
    });
  });

  // ------------------------------------------ AI Musical Director / LLM Brain ---
  const btnToggleLlmCfg = document.getElementById("btn-toggle-llm-cfg");
  const llmConfigPanel = document.getElementById("llm-config-panel");
  const llmProviderSelect = document.getElementById("llm-provider-select");
  const llmModelInput = document.getElementById("llm-model-input");
  const llmApiKeyInput = document.getElementById("llm-api-key-input");
  const llmBaseUrlInput = document.getElementById("llm-base-url-input");
  const llmKeyRow = document.getElementById("llm-key-row");
  const llmUrlRow = document.getElementById("llm-url-row");
  const btnTestLlm = document.getElementById("btn-test-llm");
  const btnSaveLlmCfg = document.getElementById("btn-save-llm-cfg");
  const llmTestBadge = document.getElementById("llm-test-badge");
  const btnLlmCompose = document.getElementById("btn-llm-compose");
  const blueprintCard = document.getElementById("blueprint-card");

  async function loadLlmConfig() {
    try {
      const cfg = await api("/api/intelligence/config");
      if (llmProviderSelect) llmProviderSelect.value = cfg.provider || "offline";
      if (llmModelInput) {
        if (cfg.provider === "nvidia") llmModelInput.value = cfg.nvidia_model || "meta/llama-3.1-70b-instruct";
        else if (cfg.provider === "ollama") llmModelInput.value = cfg.ollama_model || "llama3";
        else if (cfg.provider === "lm_studio") llmModelInput.value = cfg.lm_studio_model || "local-model";
        else if (cfg.provider === "openai") llmModelInput.value = cfg.openai_model || "gpt-4o-mini";
      }
      if (llmBaseUrlInput) {
        if (cfg.provider === "ollama") llmBaseUrlInput.value = cfg.ollama_url || "http://127.0.0.1:11434";
        else if (cfg.provider === "lm_studio") llmBaseUrlInput.value = cfg.lm_studio_url || "http://127.0.0.1:1234/v1";
        else if (cfg.provider === "openai") llmBaseUrlInput.value = cfg.openai_base_url || "https://api.openai.com/v1";
      }
      updateLlmFieldVisibility();
    } catch (e) {
      console.log("Could not load LLM config:", e);
    }
  }

  function updateLlmFieldVisibility() {
    const prov = llmProviderSelect ? llmProviderSelect.value : "offline";
    if (prov === "nvidia" || prov === "openai") {
      if (llmKeyRow) llmKeyRow.style.display = "block";
      if (llmUrlRow) llmUrlRow.style.display = (prov === "openai") ? "block" : "none";
    } else if (prov === "ollama" || prov === "lm_studio") {
      if (llmKeyRow) llmKeyRow.style.display = "none";
      if (llmUrlRow) llmUrlRow.style.display = "block";
    } else {
      if (llmKeyRow) llmKeyRow.style.display = "none";
      if (llmUrlRow) llmUrlRow.style.display = "none";
    }
  }

  if (llmProviderSelect) {
    llmProviderSelect.addEventListener("change", () => {
      updateLlmFieldVisibility();
      const prov = llmProviderSelect.value;
      if (prov === "ollama") {
        if (llmBaseUrlInput) llmBaseUrlInput.value = "http://127.0.0.1:11434";
        if (llmModelInput) llmModelInput.value = "llama3";
      } else if (prov === "lm_studio") {
        if (llmBaseUrlInput) llmBaseUrlInput.value = "http://127.0.0.1:1234/v1";
        if (llmModelInput) llmModelInput.value = "local-model";
      } else if (prov === "nvidia") {
        if (llmModelInput) llmModelInput.value = "meta/llama-3.1-70b-instruct";
      }
    });
  }

  if (btnToggleLlmCfg && llmConfigPanel) {
    btnToggleLlmCfg.addEventListener("click", () => {
      llmConfigPanel.classList.toggle("open");
      btnToggleLlmCfg.textContent = llmConfigPanel.classList.contains("open") ? "Hide LLM Engine" : "Configure LLM Engine";
    });
  }

  document.getElementById("tag-llama")?.addEventListener("click", () => { if (llmModelInput) llmModelInput.value = "meta/llama-3.1-70b-instruct"; });
  document.getElementById("tag-nemotron")?.addEventListener("click", () => { if (llmModelInput) llmModelInput.value = "nvidia/nemotron-4-340b-instruct"; });
  document.getElementById("tag-deepseek")?.addEventListener("click", () => { if (llmModelInput) llmModelInput.value = "deepseek-ai/deepseek-coder-33b-instruct"; });
  document.getElementById("tag-glm")?.addEventListener("click", () => { if (llmModelInput) llmModelInput.value = "THUDM/glm-4-9b-chat"; });

  async function saveLlmConfigSilently() {
    const prov = llmProviderSelect ? llmProviderSelect.value : "offline";
    const body = { provider: prov };
    if (prov === "nvidia") {
      if (llmApiKeyInput && llmApiKeyInput.value) body.nvidia_api_key = llmApiKeyInput.value;
      if (llmModelInput && llmModelInput.value) body.nvidia_model = llmModelInput.value;
    } else if (prov === "ollama") {
      if (llmBaseUrlInput && llmBaseUrlInput.value) body.ollama_url = llmBaseUrlInput.value;
      if (llmModelInput && llmModelInput.value) body.ollama_model = llmModelInput.value;
    } else if (prov === "lm_studio") {
      if (llmBaseUrlInput && llmBaseUrlInput.value) body.lm_studio_url = llmBaseUrlInput.value;
      if (llmModelInput && llmModelInput.value) body.lm_studio_model = llmModelInput.value;
    } else if (prov === "openai") {
      if (llmApiKeyInput && llmApiKeyInput.value) body.openai_api_key = llmApiKeyInput.value;
      if (llmBaseUrlInput && llmBaseUrlInput.value) body.openai_base_url = llmBaseUrlInput.value;
      if (llmModelInput && llmModelInput.value) body.openai_model = llmModelInput.value;
    }
    await api("/api/intelligence/config", { method: "POST", body });
  }

  if (btnTestLlm) {
    btnTestLlm.addEventListener("click", async () => {
      const prov = llmProviderSelect.value;
      btnTestLlm.disabled = true;
      btnTestLlm.textContent = "Testing...";
      if (llmTestBadge) {
        llmTestBadge.textContent = "Connecting...";
        llmTestBadge.style.background = "#fff3e0";
        llmTestBadge.style.color = "#e65100";
      }

      await saveLlmConfigSilently();

      try {
        const res = await api("/api/intelligence/test", {
          method: "POST",
          body: { provider: prov }
        });
        if (res.success) {
          if (llmTestBadge) {
            llmTestBadge.textContent = "Connected & Ready";
            llmTestBadge.style.background = "#e8f5e9";
            llmTestBadge.style.color = "#2e7d32";
          }
        } else {
          if (llmTestBadge) {
            llmTestBadge.textContent = "Failed";
            llmTestBadge.style.background = "#ffebee";
            llmTestBadge.style.color = "#c62828";
          }
          alert(res.error || "Connection failed. Please check endpoint or API key.");
        }
      } catch (err) {
        if (llmTestBadge) {
          llmTestBadge.textContent = "Error";
          llmTestBadge.style.background = "#ffebee";
          llmTestBadge.style.color = "#c62828";
        }
        alert("Test error: " + err.message);
      } finally {
        btnTestLlm.disabled = false;
        btnTestLlm.textContent = "Test Connection";
      }
    });
  }

  if (btnSaveLlmCfg) {
    btnSaveLlmCfg.addEventListener("click", async () => {
      btnSaveLlmCfg.disabled = true;
      try {
        await saveLlmConfigSilently();
        alert("LLM Intelligence configuration saved!");
      } catch (err) {
        alert("Error saving config: " + err.message);
      } finally {
        btnSaveLlmCfg.disabled = false;
      }
    });
  }

  if (btnLlmCompose) {
    btnLlmCompose.addEventListener("click", async () => {
      const prompt = promptInput.value.trim() || currentGenre;
      btnLlmCompose.disabled = true;
      btnLlmCompose.innerHTML = '<span class="dot dot-run"></span> Composing Blueprint...';

      try {
        const res = await api("/api/intelligence/compose", {
          method: "POST",
          body: { prompt, genre_hint: currentGenre }
        });

        const bp = res.blueprint;
        if (bp) {
          const titleInput = document.getElementById("title-input");
          if (titleInput && bp.title) titleInput.value = bp.title;

          if (lyricsTextarea && bp.lyrics) {
            lyricsTextarea.value = bp.lyrics;
            btnModeCustom?.click();
          }

          if (bpmInput && bp.bpm) bpmInput.value = bp.bpm;
          if (keySelect && bp.key) keySelect.value = bp.key;

          if (blueprintCard) {
            blueprintCard.classList.add("active");
            document.getElementById("blueprint-title").textContent = `${bp.title} Blueprint`;
            document.getElementById("bp-chords").textContent = `Chords: ${bp.chord_progression || 'Am - F - C - G'}`;
            document.getElementById("bp-tempo").textContent = `Tempo: ${bp.bpm || 120} BPM`;
            document.getElementById("bp-key").textContent = `Key: ${bp.key || 'C Major'}`;
            document.getElementById("bp-tone").textContent = `Tone: ${bp.tone || 'Dynamic & Melodic'}`;
          }
        }
      } catch (err) {
        alert("Blueprint composition failed: " + err.message);
      } finally {
        btnLlmCompose.disabled = false;
        btnLlmCompose.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg> Auto-Compose Blueprint';
      }
    });
  }

  loadLlmConfig();

  // -------------------------------- Direct Hugging Face Download & Model Manager ---
  const hfRepoInput = document.getElementById("hf-repo-input");
  const btnHfDownload = document.getElementById("btn-hf-download");
  const hfDlProgressBox = document.getElementById("hf-dl-progress-box");
  const hfDlStatusText = document.getElementById("hf-dl-status-text");
  const hfDlPct = document.getElementById("hf-dl-pct");
  const hfDlBarFill = document.getElementById("hf-dl-bar-fill");
  const installedModelsList = document.getElementById("installed-models-list");
  const btnRefreshModels = document.getElementById("btn-refresh-models");
  const badgeActiveModelView = document.getElementById("badge-active-model-view");

  document.querySelectorAll(".hf-preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (hfRepoInput) hfRepoInput.value = btn.dataset.repo;
    });
  });

  async function loadInstalledModels() {
    try {
      const res = await api("/api/models/installed");
      const models = res.models || [];
      const runtime = res.runtime || {};

      if (badgeActiveModelView) {
        badgeActiveModelView.textContent = `Active: ${runtime.active_model} (${runtime.hardware_mode.toUpperCase()})`;
      }

      if (!installedModelsList) return;
      if (models.length === 0) {
        installedModelsList.innerHTML = `<div style="color:var(--dim); font-size:12px; padding:12px; text-align:center;">No models installed in storage/models.</div>`;
        return;
      }

      installedModelsList.innerHTML = models.map(m => {
        const isActive = m.id === runtime.active_model;
        const sizeFormatted = m.size_mb > 0 ? (m.size_mb >= 1000 ? (m.size_mb/1024).toFixed(2) + ' GB' : m.size_mb + ' MB') : 'Built-in (0 MB)';
        return `
          <div class="installed-item">
            <div>
              <div style="font-weight:600; font-size:12.5px; display:flex; align-items:center; gap:8px;">
                <span>${escapeHtml(m.name)}</span>
                ${isActive ? '<span class="badge" style="background:#e8f5e9; color:#2e7d32; font-size:10.5px; padding:2px 6px;">Active In Studio</span>' : ''}
              </div>
              <div style="font-size:11px; color:var(--muted); margin-top:2px;">
                Storage: <code>${escapeHtml(m.path)}</code> &bull; Size: ${sizeFormatted} &bull; Mode: ${m.recommended_mode}
              </div>
              <div style="font-size:11.5px; color:var(--text-dim); margin-top:4px;">${escapeHtml(m.description)}</div>
            </div>
            <div>
              ${isActive ? '<button class="btn-secondary" style="font-size:11px; padding:5px 10px;" disabled>Active</button>' : `<button class="btn-primary" style="font-size:11px; width:auto; padding:5px 12px;" onclick="activateModel('${escapeHtml(m.id)}')">Activate Model</button>`}
            </div>
          </div>
        `;
      }).join("");
    } catch (e) {
      console.log("Failed to load installed models:", e);
    }
  }

  window.activateModel = async (modelId) => {
    try {
      await api("/api/models/activate", {
        method: "POST",
        body: { model_id: modelId }
      });
      await loadInstalledModels();
      alert(`Model "${modelId}" activated for studio synthesis!`);
    } catch (err) {
      alert("Failed to activate model: " + err.message);
    }
  };

  btnRefreshModels?.addEventListener("click", loadInstalledModels);

  async function pollHfDownload() {
    try {
      const data = await api("/api/models/status");
      const st = data.download_state;
      if (st && st.is_downloading) {
        if (hfDlProgressBox) hfDlProgressBox.style.display = "block";
        if (btnHfDownload) btnHfDownload.disabled = true;
        if (hfDlStatusText) hfDlStatusText.textContent = st.status;
        if (hfDlPct) hfDlPct.textContent = `${st.progress}%`;
        if (hfDlBarFill) hfDlBarFill.style.width = `${st.progress}%`;
      } else if (st && st.progress === 100) {
        if (hfDlStatusText) hfDlStatusText.textContent = st.status;
        if (hfDlPct) hfDlPct.textContent = "100%";
        if (hfDlBarFill) hfDlBarFill.style.width = "100%";
        if (btnHfDownload) btnHfDownload.disabled = false;
        await loadInstalledModels();
      } else if (st && st.error) {
        if (hfDlStatusText) hfDlStatusText.textContent = `Error: ${st.error}`;
        if (btnHfDownload) btnHfDownload.disabled = false;
      }
    } catch (e) {}
  }
  setInterval(pollHfDownload, 3000);

  if (btnHfDownload) {
    btnHfDownload.addEventListener("click", async () => {
      const repoId = hfRepoInput.value.trim();
      if (!repoId) {
        alert("Please enter a Hugging Face repository ID!");
        return;
      }
      btnHfDownload.disabled = true;
      if (hfDlProgressBox) hfDlProgressBox.style.display = "block";
      if (hfDlStatusText) hfDlStatusText.textContent = `Starting download for ${repoId}...`;
      if (hfDlPct) hfDlPct.textContent = "5%";
      if (hfDlBarFill) hfDlBarFill.style.width = "5%";

      try {
        await api("/api/models/download", {
          method: "POST",
          body: { repo_id: repoId }
        });
        pollHfDownload();
      } catch (err) {
        alert("Download failed: " + err.message);
        btnHfDownload.disabled = false;
      }
    });
  }

  loadInstalledModels();

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Load initial tracks
  await loadTracks();
});

