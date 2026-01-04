const bridge = async (path, method = "GET", data = null) => {
  const response = await fetch("/bridge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, method, data }),
  });
  if (!response.ok) {
    throw new Error(`Bridge error: ${response.status}`);
  }
  return response.json();
};

const $ = (id) => document.getElementById(id);

const loadConfig = async () => {
  const config = await bridge("/api/config");
  $("displaySelect").value = config.display_id;
  $("previewInterval").value = config.preview_interval_sec;
  $("darkThreshold").value = config.dark_threshold;
  $("saturationBoost").value = config.saturation_boost;
  $("zoneX").value = config.zone.x;
  $("zoneY").value = config.zone.y;
  $("zoneW").value = config.zone.width;
  $("zoneH").value = config.zone.height;
};

const saveConfig = async () => {
  const payload = {
    display_id: parseInt($("displaySelect").value, 10),
    preview_interval_sec: parseFloat($("previewInterval").value),
    dark_threshold: parseFloat($("darkThreshold").value),
    saturation_boost: parseFloat($("saturationBoost").value),
    analysis_hz: 25,
    zone: {
      x: parseInt($("zoneX").value, 10),
      y: parseInt($("zoneY").value, 10),
      width: parseInt($("zoneW").value, 10),
      height: parseInt($("zoneH").value, 10),
    },
  };
  await bridge("/api/config", "PUT", payload);
};

const refreshDiagnostics = async () => {
  const status = await bridge("/api/status");
  $("diagnostics").textContent = JSON.stringify(status, null, 2);
};

const loadDisplays = async () => {
  const displays = await bridge("/api/displays");
  $("displaySelect").innerHTML = "";
  displays.forEach((d) => {
    const option = document.createElement("option");
    option.value = d.id;
    option.textContent = d.name;
    $("displaySelect").appendChild(option);
  });
};

const savePreset = async () => {
  const name = $("presetName").value.trim();
  if (!name) return;
  const config = await bridge("/api/config");
  const payload = { name, ...config };
  await bridge("/api/presets", "POST", payload);
};

const loadPreset = async () => {
  const name = $("presetName").value.trim();
  if (!name) return;
  await bridge(`/api/presets/${name}/load`, "POST", {});
  await loadConfig();
};

const deletePreset = async () => {
  const name = $("presetName").value.trim();
  if (!name) return;
  await bridge(`/api/presets/${name}`, "DELETE", {});
};

window.addEventListener("DOMContentLoaded", async () => {
  $("preview").src = "/preview";
  await loadDisplays();
  await loadConfig();
  await refreshDiagnostics();
  setInterval(refreshDiagnostics, 1000);

  $("startBtn").addEventListener("click", () => bridge("/api/sync/start", "POST", {}));
  $("pauseBtn").addEventListener("click", () => bridge("/api/sync/pause", "POST", {}));
  $("resumeBtn").addEventListener("click", () => bridge("/api/sync/resume", "POST", {}));
  $("stopBtn").addEventListener("click", () => bridge("/api/sync/stop", "POST", {}));
  $("saveConfigBtn").addEventListener("click", saveConfig);
  $("savePresetBtn").addEventListener("click", savePreset);
  $("loadPresetBtn").addEventListener("click", loadPreset);
  $("deletePresetBtn").addEventListener("click", deletePreset);
});
