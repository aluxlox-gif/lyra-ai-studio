"use strict";

const ENGINE_META = {
  image: { icon: "▧", description: "Pembuatan gambar, character sheet, visual referensi, dan storyboard." },
  video: { icon: "▶", description: "Perencanaan adegan, aset, kontinuitas, dan produksi video." },
  voice: { icon: "♫", description: "Adapter layanan suara dan kemampuan audio." },
  voicebox: { icon: "♫", description: "Integrasi Voicebox untuk sintesis suara dan profil suara." },
  openmontage: { icon: "▱", description: "Integrasi assembly dan penyuntingan media." },
  hermes: { icon: "✧", description: "Agent bridge untuk chat dan orkestrasi kemampuan." },
  story: { icon: "▤", description: "Kerangka pipeline pengembangan cerita dan produksi film." }
};

const STATUS_LABELS = {
  connected: "TERHUBUNG", ok: "AKTIF", healthy: "SEHAT",
  adapter_available: "ADAPTER TERSEDIA",
  configuration_required: "PERLU KONFIGURASI",
  planned: "DIRANCANG", pending: "MENUNGGU",
  unavailable: "TIDAK TERSEDIA", unreachable: "TIDAK TERJANGKAU",
  upstream_error: "ERROR LAYANAN", invalid_response: "RESPONS TIDAK VALID"
};

function activateView(viewId) {
  const panels = [...document.querySelectorAll(".view-panel")];
  const target = panels.find(panel => panel.id === viewId) || panels.find(panel => panel.id === "dashboard");
  if (!target) return;

  panels.forEach(panel => {
    const selected = panel === target;
    panel.classList.toggle("active", selected);
    panel.hidden = !selected;
  });

  document.querySelectorAll("[data-view]").forEach(link => {
    const selected = link.dataset.view === target.id;
    link.classList.toggle("active", selected && link.classList.contains("nav-item"));
    if (link.classList.contains("nav-item")) {
      if (selected) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    }
  });

  document.getElementById("page-title").textContent = target.dataset.title || "LYRA AI STUDIO";
  document.getElementById("page-description").textContent = target.dataset.description || "";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function labelForStatus(status, connected) {
  if (connected === true) return "TERHUBUNG";
  if (connected === false && (!status || status === "connected")) return "BELUM TERHUBUNG";
  return STATUS_LABELS[String(status || "").toLowerCase()] || String(status || "STATUS TIDAK DIKETAHUI").replaceAll("_", " ").toUpperCase();
}

function statusClass(status, connected) {
  if (connected === true || ["healthy", "connected", "ok"].includes(String(status || "").toLowerCase())) return "good";
  if (["planned", "pending", "adapter_available", "configuration_required"].includes(String(status || "").toLowerCase())) return "neutral";
  return "bad";
}

const SETTINGS_KEY = "lyra.settings";
const ENGINES_CACHE_KEY = "lyra.cache.engines";

function loadSettings() {
  try {
    return JSON.parse(window.localStorage.getItem(SETTINGS_KEY)) || {};
  } catch {
    return {};
  }
}

function saveSettings(settings) {
  window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

function apiBase() {
  const base = String(loadSettings().apiBaseUrl || "").trim();
  return base.replace(/\/+$/, "");
}

async function getJson(path) {
  const response = await fetch(apiBase() + path, {
    method: "GET",
    headers: { "Accept": "application/json" },
    cache: "no-store"
  });
  if (!response.ok) throw new Error(path + " returned HTTP " + response.status);
  return response.json();
}

function cacheEngines(engines) {
  try {
    window.localStorage.setItem(ENGINES_CACHE_KEY, JSON.stringify({
      engines, savedAt: new Date().toISOString()
    }));
  } catch { /* storage full/blocked: offline snapshot is best-effort */ }
}

function cachedEngines() {
  try {
    return JSON.parse(window.localStorage.getItem(ENGINES_CACHE_KEY));
  } catch {
    return null;
  }
}

function makeEngineCard(id, engine) {
  const meta = ENGINE_META[id] || { icon: "◇", description: "Engine terdaftar pada backend." };
  const status = engine && engine.status;
  const connected = engine && engine.connected === true;
  const card = document.createElement("article");
  card.className = "engine-card";

  const top = document.createElement("div");
  top.className = "engine-card-top";
  const icon = document.createElement("div");
  icon.className = "engine-icon";
  icon.textContent = meta.icon;
  const badge = document.createElement("span");
  badge.className = "status-pill " + statusClass(status, connected);
  badge.textContent = labelForStatus(status, connected);
  top.append(icon, badge);

  const title = document.createElement("h3");
  title.textContent = (engine && engine.name) || id;
  const description = document.createElement("p");
  description.textContent = meta.description;
  const technical = document.createElement("small");
  technical.className = "technical-status";
  technical.textContent = "ID: " + id + " · status: " + (status || "unknown");

  card.append(top, title, description, technical);
  return card;
}

function renderEngines(engines) {
  const grid = document.getElementById("engine-grid");
  grid.replaceChildren();
  const entries = Object.entries(engines || {});
  if (!entries.length) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = "Backend belum mengembalikan data engine.";
    grid.append(empty);
    return;
  }
  entries.forEach(([id, engine]) => grid.append(makeEngineCard(id, engine || {})));
  document.getElementById("engine-count").textContent = String(entries.length);
  document.getElementById("connected-count").textContent =
    String(entries.filter(([, engine]) => engine && engine.connected === true).length);
  const story = engines.story;
  setPill("story-state", story ? labelForStatus(story.status, story.connected) : "TIDAK TERDAFTAR",
    story ? statusClass(story.status, story.connected) : "bad");
}

function setPill(id, label, tone) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = label;
  el.className = "status-pill " + tone;
}

function setConnection(id, detailId, data, error) {
  if (error || !data) {
    setPill(id, "TIDAK TERJANGKAU", "bad");
    document.getElementById(detailId).textContent = error ? error.message : "Tidak ada respons.";
    return;
  }
  setPill(id, labelForStatus(data.status, data.connected), statusClass(data.status, data.connected));
  document.getElementById(detailId).textContent = data.connected
    ? "Koneksi berhasil" + (data.status_code ? " (HTTP " + data.status_code + ")" : "")
    : (data.status || data.message || "Belum terhubung");
}

async function refreshDashboard() {
  const button = document.getElementById("refresh-button");
  button.disabled = true;
  button.classList.add("is-loading");
  try {
    const tasks = await Promise.allSettled([
      getJson("/api/health"),
      getJson("/api/engines"),
      getJson("/api/engines/voicebox/health"),
      getJson("/api/agents/hermes/health")
    ]);

    const [healthResult, enginesResult, voiceResult, hermesResult] = tasks;
    const health = healthResult.status === "fulfilled" ? healthResult.value : null;

    if (health) {
      document.getElementById("backend-state").textContent = "ONLINE";
      document.getElementById("backend-detail").textContent =
        (health.app || "LYRA AI STUDIO") + " · v" + (health.version || "—");
      document.getElementById("version-badge").textContent = "VERSION " + (health.version || "—");
      document.getElementById("connection-label").textContent = "Backend terhubung";
      document.getElementById("sidebar-dot").classList.add("online");
      document.getElementById("system-status").textContent = "Backend online";
    } else {
      document.getElementById("backend-state").textContent = "OFFLINE";
      document.getElementById("backend-detail").textContent = healthResult.reason?.message || "Health check gagal";
      document.getElementById("connection-label").textContent =
        navigator.onLine === false ? "Mode offline" : "Backend tidak tersedia";
      document.getElementById("sidebar-dot").classList.remove("online");
      document.getElementById("system-status").textContent = "Backend connection failed";
    }

    if (enginesResult.status === "fulfilled") {
      renderEngines(enginesResult.value);
      cacheEngines(enginesResult.value);
    } else {
      const snapshot = cachedEngines();
      if (snapshot && snapshot.engines) {
        renderEngines(snapshot.engines);
        document.getElementById("system-status").textContent =
          "Mode offline — data engine terakhir dari " +
          new Intl.DateTimeFormat("id-ID", { hour: "2-digit", minute: "2-digit" })
            .format(new Date(snapshot.savedAt));
      } else {
        document.getElementById("engine-grid").replaceChildren();
        const error = document.createElement("p");
        error.className = "error-message";
        error.textContent = "Gagal memuat /api/engines: " + enginesResult.reason.message;
        document.getElementById("engine-grid").append(error);
        document.getElementById("engine-count").textContent = "—";
        document.getElementById("connected-count").textContent = "—";
      }
    }

    setConnection("voicebox-state", "voicebox-detail",
      voiceResult.status === "fulfilled" ? voiceResult.value : null,
      voiceResult.status === "rejected" ? voiceResult.reason : null);
    setConnection("hermes-state", "hermes-detail",
      hermesResult.status === "fulfilled" ? hermesResult.value : null,
      hermesResult.status === "rejected" ? hermesResult.reason : null);

    document.getElementById("last-checked").textContent =
      new Intl.DateTimeFormat("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date());
  } finally {
    button.disabled = false;
    button.classList.remove("is-loading");
  }
}

function initSettings() {
  const form = document.getElementById("settings-form");
  if (!form) return;
  const fields = {
    apiBaseUrl: document.getElementById("setting-api-base"),
    internalToken: document.getElementById("setting-internal-token"),
    hermesToken: document.getElementById("setting-hermes-token"),
    voiceProfileId: document.getElementById("setting-voice-profile")
  };
  const settings = loadSettings();
  Object.entries(fields).forEach(([key, input]) => {
    if (input) input.value = settings[key] || "";
  });
  const feedback = document.getElementById("settings-feedback");
  form.addEventListener("submit", event => {
    event.preventDefault();
    const next = {};
    Object.entries(fields).forEach(([key, input]) => {
      if (input) next[key] = input.value.trim();
    });
    saveSettings(next);
    feedback.textContent = "Tersimpan di perangkat ini.";
    refreshDashboard();
  });
  document.getElementById("settings-clear").addEventListener("click", () => {
    window.localStorage.removeItem(SETTINGS_KEY);
    Object.values(fields).forEach(input => { if (input) input.value = ""; });
    feedback.textContent = "Pengaturan dihapus.";
  });
  const mode = document.getElementById("settings-mode");
  const updateMode = () => {
    mode.textContent = navigator.onLine ? "Online" : "Offline (fitur dasar)";
  };
  updateMode();
  window.addEventListener("online", updateMode);
  window.addEventListener("offline", updateMode);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("a[data-view]").forEach(link => {
    link.addEventListener("click", event => {
      event.preventDefault();
      const viewId = link.dataset.view;
      if (!viewId) return;
      if (window.location.hash !== "#" + viewId) {
        window.history.pushState({ viewId }, "", "#" + viewId);
      }
      activateView(viewId);
    });
  });

  window.addEventListener("popstate", () => activateView(window.location.hash.slice(1) || "dashboard"));
  activateView(window.location.hash.slice(1) || "dashboard");
  document.getElementById("refresh-button").addEventListener("click", refreshDashboard);
  initSettings();
  refreshDashboard();
  window.setInterval(refreshDashboard, 30000);

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // Offline shell is a progressive enhancement; the app
      // still runs normally without it.
    });
  }
});
