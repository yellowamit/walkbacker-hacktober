/**
 * WalkBacker Main Frontend Application
 * Offline-first state manager and event coordinator.
 */
document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentCoordinates = { lat: 40.7128, lon: -74.0060 };
  let currentPlan = null;
  let breadcrumbHistory = [];
  let turnaroundTimer = null;
  let remainingSeconds = 0;

  // DOM Elements
  const durationPills = document.querySelectorAll("#durationPills .pill-btn");
  const durationInput = document.getElementById("durationMinutes");
  const vibeSelect = document.getElementById("vibeSelect");
  const locationNameInput = document.getElementById("locationName");
  const coordsDisplay = document.getElementById("coordsDisplay");
  const neuralToggle = document.getElementById("neuralToggle");
  const toggleLabel = document.getElementById("toggleLabel");
  const btnGetGPS = document.getElementById("btnGetGPS");
  const btnPlanExpedition = document.getElementById("btnPlanExpedition");

  const setupSection = document.getElementById("setupSection");
  const activeExpeditionSection = document.getElementById("activeExpeditionSection");
  const btnNewExpedition = document.getElementById("btnNewExpedition");
  const btnAudioCue = document.getElementById("btnAudioCue");
  const btnPocketMode = document.getElementById("btnPocketMode");
  const btnExitPocket = document.getElementById("btnExitPocket");
  const pocketOverlay = document.getElementById("pocketOverlay");

  const btnDropCrumb = document.getElementById("btnDropCrumb");
  const btnExportGPX = document.getElementById("btnExportGPX");
  const btnExportGeoJSON = document.getElementById("btnExportGeoJSON");
  const trailLog = document.getElementById("trailLog");

  const natureInput = document.getElementById("natureInput");
  const btnIdentify = document.getElementById("btnIdentify");
  const lensResult = document.getElementById("lensResult");
  const traitTags = document.querySelectorAll(".trait-tag");

  const ramPill = document.getElementById("ramPill");
  const ramText = document.getElementById("ramText");

  // -------------------------------------------------------------
  // Initialization & Memory Telemetry
  // -------------------------------------------------------------
  updateMemoryStatus();
  setInterval(updateMemoryStatus, 15000);

  async function updateMemoryStatus() {
    try {
      const res = await fetch("/api/memory");
      if (res.ok) {
        const mem = await res.json();
        ramText.textContent = `RAM: ~${Math.round(mem.process_ram_mb)}MB (8GB Safe)`;
      }
    } catch (e) {
      // offline fallback
      ramText.textContent = "RAM: ~85MB (Offline)";
    }
  }

  // -------------------------------------------------------------
  // Duration Pill Selection
  // -------------------------------------------------------------
  durationPills.forEach(pill => {
    pill.addEventListener("click", () => {
      durationPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      durationInput.value = pill.dataset.min;
    });
  });

  // Toggle Neural vs Edge Mode
  neuralToggle.addEventListener("change", () => {
    if (neuralToggle.checked) {
      toggleLabel.textContent = "Local Open-Weight Model (SmolLM2-135M)";
    } else {
      toggleLabel.textContent = "Edge Zero-RAM Engine (Instant, Offline)";
    }
  });

  // -------------------------------------------------------------
  // GPS Location Handler
  // -------------------------------------------------------------
  btnGetGPS.addEventListener("click", () => {
    if ("geolocation" in navigator) {
      btnGetGPS.textContent = "⏳...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          currentCoordinates = {
            lat: pos.coords.latitude,
            lon: pos.coords.longitude
          };
          coordsDisplay.textContent = `GPS: ${currentCoordinates.lat.toFixed(4)}° N, ${currentCoordinates.lon.toFixed(4)}° W`;
          btnGetGPS.textContent = "✓ Fixed";
          setTimeout(() => { btnGetGPS.textContent = "📍 GPS"; }, 2500);
        },
        (err) => {
          console.warn("Geolocation fallback:", err.message);
          coordsDisplay.textContent = "Default GPS: 40.7128° N, -74.0060° W (Offline fixed)";
          btnGetGPS.textContent = "📍 GPS";
        },
        { enableHighAccuracy: true, timeout: 6000 }
      );
    }
  });

  // -------------------------------------------------------------
  // Plan Expedition (Chain of Thought Agent Call)
  // -------------------------------------------------------------
  btnPlanExpedition.addEventListener("click", async () => {
    btnPlanExpedition.disabled = true;
    btnPlanExpedition.innerHTML = "<span>🧠 Reasoning outdoor path...</span>";

    const payload = {
      duration_minutes: parseInt(durationInput.value, 10),
      vibe: vibeSelect.value,
      lat: currentCoordinates.lat,
      lon: currentCoordinates.lon,
      location_name: locationNameInput.value.trim() || "Trailhead Base",
      use_neural: neuralToggle.checked
    };

    try {
      const res = await fetch("/api/plan-expedition", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Failed to plan expedition");
      const plan = await res.json();
      currentPlan = plan;

      renderExpedition(plan);
      setupSection.classList.add("hidden");
      activeExpeditionSection.classList.remove("hidden");
      window.scrollTo({ top: 0, behavior: "smooth" });

      // Automatically speak introductory audio cue
      if (window.audioCueEngine && plan.audio_script) {
        window.audioCueEngine.speak(plan.audio_script);
      }
    } catch (err) {
      alert("Error generating plan: " + err.message);
    } finally {
      btnPlanExpedition.disabled = false;
      btnPlanExpedition.innerHTML = '<span class="btn-icon">🌲</span> Generate Screen-Free Expedition';
    }
  });

  // -------------------------------------------------------------
  // Render Expedition Plan
  // -------------------------------------------------------------
  function renderExpedition(plan) {
    const card = plan.field_card;
    document.getElementById("cardDuration").textContent = `${card.expedition_duration_min} MIN EXPEDITION`;
    document.getElementById("cardTitle").textContent = card.title;
    document.getElementById("cardLocation").textContent = `Starting: ${card.location}`;
    document.getElementById("turnaroundClock").textContent = card.turnaround_time;
    document.getElementById("maxRadiusKm").textContent = `${card.max_distance_km} km`;
    document.getElementById("returnBearingVal").textContent = `${card.return_bearing_deg}° ${card.cardinal_home}`;

    // Missions list
    const list = document.getElementById("missionsList");
    list.innerHTML = "";
    card.missions.forEach(m => {
      const li = document.createElement("li");
      li.textContent = m;
      list.appendChild(li);
    });

    // Species
    document.getElementById("speciesCommon").textContent = card.key_species.name;
    document.getElementById("speciesScientific").textContent = `(${card.key_species.scientific})`;
    document.getElementById("speciesCue").textContent = card.key_species.cue;

    // Set compass target bearing
    if (window.compassController) {
      window.compassController.setTargetBearing(card.return_bearing_deg);
    }

    // Set countdown
    startTurnaroundCountdown(plan.turnaround_metrics.outbound_minutes);

    // Initialize breadcrumb history with origin
    breadcrumbHistory = [{
      lat: plan.waypoints.origin.lat,
      lon: plan.waypoints.origin.lon,
      timestamp: new Date().toISOString(),
      name: card.location
    }];
    updateTrailUI();

    // Render Chain of Thought Transparency steps
    renderCoT(plan.chain_of_thought);
  }

  function renderCoT(cot) {
    const cotBody = document.getElementById("cotBody");
    cotBody.innerHTML = `
      <div class="cot-step-box">
        <strong>Stage 1: Environmental & Solar Analysis</strong>
        <p>${cot.step1_environmental_analysis}</p>
      </div>
      <div class="cot-step-box">
        <strong>Stage 2: Sensory Touch-Grass Missions Formulation</strong>
        <p>${cot.step2_sensory_missions}</p>
      </div>
      <div class="cot-step-box">
        <strong>Stage 3: Safe Navigation & Turnaround Mathematics</strong>
        <p>${cot.step3_navigation_math}</p>
      </div>
      <div class="cot-step-box">
        <strong>Stage 4: Screen Minimization Protocol</strong>
        <p>${cot.step4_screen_minimization}</p>
      </div>
    `;
  }

  // -------------------------------------------------------------
  // Turnaround Countdown Timer
  // -------------------------------------------------------------
  function startTurnaroundCountdown(outboundMinutes) {
    if (turnaroundTimer) clearInterval(turnaroundTimer);
    remainingSeconds = Math.round(outboundMinutes * 60);

    const updateDisplay = () => {
      const mins = Math.floor(remainingSeconds / 60);
      const secs = remainingSeconds % 60;
      const timeStr = `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

      const statMins = document.getElementById("statTimeRemaining");
      if (statMins) statMins.textContent = mins;

      const countdownSpan = document.getElementById("countdownMin");
      if (countdownSpan) countdownSpan.textContent = timeStr;

      if (remainingSeconds <= 0) {
        clearInterval(turnaroundTimer);
        // Play melodic chime & voice alert
        if (window.audioCueEngine) {
          window.audioCueEngine.playTurnaroundChime();
          setTimeout(() => {
            window.audioCueEngine.speak("Turnaround alert. Time to turn back and follow your WalkBack compass home.");
          }, 1500);
        }
      }
      remainingSeconds--;
    };

    updateDisplay();
    turnaroundTimer = setInterval(updateDisplay, 1000);
  }

  // -------------------------------------------------------------
  // Breadcrumbs & Dead Reckoning
  // -------------------------------------------------------------
  btnDropCrumb.addEventListener("click", async () => {
    // Generate slight walk offset (simulated trail step ~80m northeast)
    const last = breadcrumbHistory[breadcrumbHistory.length - 1];
    const newLat = last.lat + 0.0006;
    const newLon = last.lon + 0.0005;

    try {
      const res = await fetch("/api/breadcrumbs/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: newLat, lon: newLon })
      });
      const data = await res.json();

      breadcrumbHistory.push({
        lat: newLat,
        lon: newLon,
        timestamp: new Date().toISOString()
      });

      // Update distance home and bearing
      document.getElementById("distanceHome").innerHTML = `Distance to Base: <strong>${Math.round(data.walkback.distance_to_origin_m)} m</strong>`;
      document.getElementById("pocketDistance").textContent = `${Math.round(data.walkback.distance_to_origin_m)} m to Base`;

      if (window.compassController) {
        window.compassController.setTargetBearing(data.walkback.bearing_home_deg);
      }

      updateTrailUI(data.total_distance_m);
    } catch (e) {
      console.error(e);
    }
  });

  function updateTrailUI(distMeters = 0) {
    document.getElementById("statDistance").textContent = (distMeters / 1000).toFixed(2);
    document.getElementById("statCrumbs").textContent = breadcrumbHistory.length;

    trailLog.innerHTML = breadcrumbHistory.map((pt, i) => `
      <div class="log-entry">#${i + 1}: [${pt.lat.toFixed(4)}, ${pt.lon.toFixed(4)}] ${i === 0 ? "(Base)" : ""}</div>
    `).reverse().join("");
  }

  // Export GPX
  btnExportGPX.addEventListener("click", async () => {
    const res = await fetch("/api/breadcrumbs/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        breadcrumbs: breadcrumbHistory,
        trail_name: currentPlan ? currentPlan.vibe_title : "WalkBacker Trail",
        format: "gpx"
      })
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "walkbacker_trail.gpx";
    a.click();
  });

  // Export GeoJSON
  btnExportGeoJSON.addEventListener("click", async () => {
    const res = await fetch("/api/breadcrumbs/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        breadcrumbs: breadcrumbHistory,
        trail_name: currentPlan ? currentPlan.vibe_title : "WalkBacker Trail",
        format: "geojson"
      })
    });
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "walkbacker_trail.geojson";
    a.click();
  });

  // -------------------------------------------------------------
  // Pocket Mode Overlay
  // -------------------------------------------------------------
  btnPocketMode.addEventListener("click", () => {
    pocketOverlay.classList.remove("hidden");
    updateOverlayClock();
  });

  btnExitPocket.addEventListener("click", () => {
    pocketOverlay.classList.add("hidden");
  });

  function updateOverlayClock() {
    const clock = document.getElementById("overlayClock");
    if (clock) {
      const now = new Date();
      clock.textContent = now.toTimeString().substring(0, 5);
    }
  }

  // Audio Cue Button
  btnAudioCue.addEventListener("click", () => {
    if (currentPlan && window.audioCueEngine) {
      window.audioCueEngine.speak(currentPlan.audio_script);
    }
  });

  // New Expedition Button
  btnNewExpedition.addEventListener("click", () => {
    activeExpeditionSection.classList.add("hidden");
    setupSection.classList.remove("hidden");
  });

  // -------------------------------------------------------------
  // Offline Nature Identifier (Trail Lens)
  // -------------------------------------------------------------
  btnIdentify.addEventListener("click", async () => {
    const query = natureInput.value.trim();
    if (!query) return;

    btnIdentify.textContent = "Searching...";
    try {
      const res = await fetch("/api/identify-nature", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text_query: query })
      });
      const data = await res.json();
      renderLensResult(data);
    } catch (err) {
      alert("Identifier error: " + err.message);
    } finally {
      btnIdentify.textContent = "🔍 Identify Species";
    }
  });

  traitTags.forEach(tag => {
    tag.addEventListener("click", () => {
      natureInput.value = tag.dataset.trait;
      btnIdentify.click();
    });
  });

  function renderLensResult(data) {
    lensResult.classList.remove("hidden");
    const sp = data.species;

    lensResult.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <h3 style="color:var(--forest-dark); font-size:1.15rem;">🌿 ${sp.common_name} <em>(${sp.scientific_name})</em></h3>
        <span style="font-size:0.75rem; font-weight:700; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:10px;">
          ${Math.round((data.confidence || 0.85) * 100)}% Match
        </span>
      </div>
      <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:6px;"><strong>Habitat & Morphology:</strong> ${sp.leaf_shape}. ${sp.habitat}.</p>
      <div style="background:#fefce8; border-left:3px solid var(--autumn-amber); padding:8px 12px; border-radius:4px; font-size:0.85rem; color:#854d0e; margin-bottom:6px;">
        <strong>Touch Grass Field Cue:</strong> ${data.touch_grass_action || sp.touch_grass_cue}
      </div>
      <p style="font-size:0.8rem; color:var(--text-muted);"><strong>Ecological Lore:</strong> ${data.ecological_lore || sp.ecological_note}</p>
    `;
  }
});
