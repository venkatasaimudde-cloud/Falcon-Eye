/**
 * FALCON EYE — Drone Telemetry & WebSocket HUD Synchronizer
 * Connects to /ws for live UAV telemetry or falls back to REST polling.
 * Explicitly displays DEMO / SIMULATION telemetry labels.
 */

let ws = null;
let pollInterval = null;

function initTelemetry() {
  connectWebSocket();
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  try {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("[+] Falcon Eye WebSocket Telemetry Connected");
      clearInterval(pollInterval);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'TELEMETRY_UPDATE') {
          if (msg.drone) applyTelemetryUpdate(msg.drone);
          if (msg.responders && window.updateMapResponders) window.updateMapResponders(msg.responders);
          if (msg.responders && window.renderResponderCards) window.renderResponderCards(msg.responders);
          if (msg.cad_messages && window.renderCadMessages) window.renderCadMessages(msg.cad_messages);
        }
      } catch (e) {
        console.error("Error processing websocket payload:", e);
      }
    };

    ws.onerror = (err) => {
      console.warn("[-] WebSocket error, falling back to polling", err);
      startPolling();
    };

    ws.onclose = () => {
      console.warn("[-] WebSocket closed, attempting reconnection in 3s");
      startPolling();
      setTimeout(connectWebSocket, 3000);
    };
  } catch (err) {
    console.error("[-] WebSocket connection failed:", err);
    startPolling();
  }
}

function startPolling() {
  if (pollInterval) return;
  pollInterval = setInterval(fetchTelemetryRest, 1500);
}

async function fetchTelemetryRest() {
  try {
    const res = await fetch('/api/drone/telemetry');
    if (res.ok) {
      const data = await res.json();
      applyTelemetryUpdate(data);
    }

    const resResp = await fetch('/api/responders/live');
    if (resResp.ok) {
      const rData = await resResp.json();
      if (window.updateMapResponders) window.updateMapResponders(rData.responders);
      if (window.renderResponderCards) window.renderResponderCards(rData.responders);
    }
  } catch (err) {
    console.error("Error polling telemetry:", err);
  }
}

function applyTelemetryUpdate(d) {
  // Update header status
  const droneStatusElem = document.getElementById('drone-status-text');
  if (droneStatusElem) {
    droneStatusElem.innerText = `${d.status} (${d.target_zone})`;
  }

  // Update HUD values
  const altElem = document.getElementById('hud-alt');
  const spdElem = document.getElementById('hud-speed');
  const batElem = document.getElementById('hud-battery');
  const hdgElem = document.getElementById('hud-heading');
  const latLonElem = document.getElementById('hud-latlon');
  const zoneElem = document.getElementById('hud-zone');

  if (altElem) altElem.innerText = `${d.altitude_m} m`;
  if (spdElem) spdElem.innerText = `${d.speed_kmh} km/h`;
  if (batElem) {
    batElem.innerText = `${Math.round(d.battery_pct)}%`;
    batElem.style.color = d.battery_pct > 25 ? '#22C55E' : '#EF4444';
  }
  if (hdgElem) hdgElem.innerText = `${Math.round(d.heading_deg)}°`;
  if (latLonElem) latLonElem.innerText = `${d.lat.toFixed(5)}° N, ${d.lon.toFixed(5)}° E`;
  if (zoneElem) zoneElem.innerText = d.target_zone;

  // Sync to Leaflet map
  if (window.updateMapDrone) {
    window.updateMapDrone(d);
  }
}

async function sendDroneCommand(action) {
  try {
    const formData = new FormData();
    formData.append('action', action);
    const res = await fetch('/api/drone/control', { method: 'POST', body: formData });
    const data = await res.json();
    if (window.showToast) {
      window.showToast(data.message);
    }
    applyTelemetryUpdate(data.telemetry);
  } catch (err) {
    console.error("Error sending drone command:", err);
  }
}

window.initTelemetry = initTelemetry;
window.sendDroneCommand = sendDroneCommand;
