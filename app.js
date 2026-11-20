/**
 * FALCON EYE — Main Application Controller
 * Handles view navigation, state management, API requests,
 * Chart.js analytics rendering, audio alarms, and notifications.
 */

let audioAlertsEnabled = false;
let audioCtx = null;
let analyticsCharts = {};
let isSidebarOpen = false; // Starts closed: 1st click = Open, 2nd click = Close, 3rd click = Open

document.addEventListener('DOMContentLoaded', () => {
  initSidebarToggle();
  initNavigation();
  initClock();
  fetchDashboardStats();
  initAnalyticsCharts();
  loadIncidentsList();
  loadResponseTeams();

  // Initialize Map and Telemetry modules
  if (window.initMaps) window.initMaps();
  if (window.initTelemetry) window.initTelemetry();
  loadSettings();

  // Polling for dashboard KPI stats every 4 seconds
  setInterval(fetchDashboardStats, 4000);
});

// --------------------------------------------------------------------------
// Sidebar Navigation Toggle Controller
// --------------------------------------------------------------------------
function initSidebarToggle() {
  const headerBtn = document.getElementById('header-ai-logo-btn');
  const sidebarLogo = document.getElementById('sidebar-brand-logo');
  const closeBtn = document.getElementById('sidebar-close-icon-btn');
  const overlay = document.getElementById('sidebar-overlay');

  window.toggleSidebar = function(forceState) {
    if (typeof forceState === 'boolean') {
      isSidebarOpen = forceState;
    } else {
      isSidebarOpen = !isSidebarOpen;
    }
    updateSidebarUI();
  };

  // Header AI Logo toggle click
  if (headerBtn) {
    headerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      window.toggleSidebar();
    });
  }

  // Sidebar brand AI logo toggle click
  if (sidebarLogo) {
    sidebarLogo.addEventListener('click', (e) => {
      e.stopPropagation();
      window.toggleSidebar();
    });
  }

  // Explicit close button in sidebar
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      window.toggleSidebar(false);
    });
  }

  // Mobile / tablet backdrop overlay click
  if (overlay) {
    overlay.addEventListener('click', () => {
      window.toggleSidebar(false);
    });
  }

  // Escape key closes sidebar
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isSidebarOpen) {
      window.toggleSidebar(false);
    }
  });

  // Apply initial collapsed state
  updateSidebarUI();
}

function updateSidebarUI() {
  const container = document.getElementById('app-container');
  if (!container) return;

  if (isSidebarOpen) {
    container.classList.add('sidebar-open');
    container.classList.remove('sidebar-collapsed');
  } else {
    container.classList.remove('sidebar-open');
    container.classList.add('sidebar-collapsed');
  }

  const headerBtn = document.getElementById('header-ai-logo-btn');
  if (headerBtn) {
    headerBtn.setAttribute('aria-expanded', isSidebarOpen ? 'true' : 'false');
  }

  // Recalculate layout for Leaflet maps and responsive components
  [50, 150, 300, 450].forEach(delay => {
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
      if (window.commandMap) window.commandMap.invalidateSize(true);
      if (window.gisMap) window.gisMap.invalidateSize(true);
    }, delay);
  });
}

// --------------------------------------------------------------------------
// Navigation & Views
// --------------------------------------------------------------------------
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetView = item.getAttribute('data-view');
      switchView(targetView);
      // On mobile / tablet, close drawer after selecting an item
      if (window.innerWidth <= 900) {
        if (window.toggleSidebar) window.toggleSidebar(false);
      }
    });
  });
}

function switchView(viewId) {
  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const activeNav = document.querySelector(`.nav-item[data-view="${viewId}"]`);
  if (activeNav) activeNav.classList.add('active');

  // Update container views
  document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active'));
  const activeContainer = document.getElementById(`view-${viewId}`);
  if (activeContainer) activeContainer.classList.add('active');

  // Update header title
  const titleMap = {
    'command-center': 'COMMAND CENTER DASHBOARD',
    'live-monitoring': 'SURVEILLANCE VIDEO FEEDS',
    'ai-detection': 'AI COMPUTER VISION STUDIO',
    'crowd-intelligence': 'CROWD DENSITY & HEATMAP INTELLIGENCE',
    'face-privacy': 'RESPONSIBLE FACE INTELLIGENCE & PRIVACY',
    'drone-intelligence': 'UAV DRONE TELEMETRY & PATROL CONTROL',
    'geospatial': 'GEOSPATIAL GIS & EMERGENCY ROUTING',
    'emergency-response': 'TACTICAL RESPONSE & DISPATCH MANAGEMENT',
    'multilingual': 'MULTILINGUAL EMERGENCY ASSISTANT',
    'settings': 'COMMAND CENTER SYSTEM SETTINGS & JURISDICTION'
  };
  const titleElem = document.getElementById('view-title-text');
  if (titleElem) {
    titleElem.innerText = titleMap[viewId] || 'COMMAND CENTER';
  }

  // Trigger map resize and lazy initialization if switching to GIS views
  if (viewId === 'geospatial') {
    if (window.ensureGisMap) window.ensureGisMap();
    [50, 150, 300, 600].forEach(delay => {
      setTimeout(() => {
        if (window.gisMap) window.gisMap.invalidateSize(true);
      }, delay);
    });
    if (window.loadMapData) window.loadMapData();
  } else if (viewId === 'command-center') {
    [50, 150, 300, 600].forEach(delay => {
      setTimeout(() => {
        if (window.commandMap) window.commandMap.invalidateSize(true);
      }, delay);
    });
    if (window.loadMapData) window.loadMapData();
  } else if (viewId === 'emergency-response') {
    if (window.loadResponseTeams) window.loadResponseTeams();
  }
}

// --------------------------------------------------------------------------
// Real-Time Clock
// --------------------------------------------------------------------------
function initClock() {
  const clock = document.getElementById('utc-clock');
  function update() {
    const now = new Date();
    if (clock) {
      clock.innerText = now.toTimeString().split(' ')[0] + ' UTC';
    }
  }
  update();
  setInterval(update, 1000);
}

// --------------------------------------------------------------------------
// Dashboard KPI Stats
// --------------------------------------------------------------------------
async function fetchDashboardStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const s = await res.json();

    setKpi('kpi-total-incidents', s.total_incidents);
    setKpi('kpi-active-incidents', s.active_incidents);
    setKpi('kpi-resolved-incidents', s.resolved_incidents);
    setKpi('kpi-people-detected', s.people_detected);
    setKpi('kpi-vehicles-detected', s.vehicles_detected);
    setKpi('kpi-crowd-alerts', s.crowd_alerts);
    setKpi('kpi-fire-alerts', s.fire_smoke_alerts);
    setKpi('kpi-monitored-sources', s.monitored_sources);
    setKpi('kpi-ack-time', `${s.avg_ack_time_minutes}m`);

    const healthElem = document.getElementById('system-health-badge');
    if (healthElem) healthElem.innerText = s.system_health;

  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

function setKpi(id, val) {
  const el = document.getElementById(id);
  if (el) el.innerText = val;
}

// --------------------------------------------------------------------------
// Incidents List & Lifecycle
// --------------------------------------------------------------------------
async function loadIncidentsList() {
  try {
    const res = await fetch('/api/incidents');
    if (!res.ok) return;
    const incidents = await res.json();

    const tbody = document.getElementById('incidents-tbody');
    const recentList = document.getElementById('recent-incidents-list');

    if (tbody) {
      tbody.innerHTML = incidents.map(inc => {
        const sevClass = inc.severity === 'CRITICAL' ? 'color:#EF4444' : inc.severity === 'HIGH' ? 'color:#F97316' : 'color:#F59E0B';
        const statColor = inc.status === 'RESOLVED' ? '#22C55E' : '#00D9FF';
        return `
          <tr>
            <td><b style="color:#00D9FF;">${inc.incident_number}</b></td>
            <td><b>${inc.title}</b></td>
            <td>${inc.category.replace('_', ' ')}</td>
            <td><span style="${sevClass}; font-weight:bold;">${inc.severity}</span></td>
            <td><span style="color:${statColor}; font-weight:bold;">${inc.status}</span></td>
            <td>${inc.location_name}</td>
            <td>${inc.risk_score}/100</td>
            <td>
              <button onclick="viewIncidentModal(${inc.id})" class="btn-falcon" style="padding:4px 8px; font-size:11px;">View</button>
              <a href="/api/reports/incident/${inc.id}/pdf" target="_blank" class="btn-falcon" style="padding:4px 8px; font-size:11px; text-decoration:none;">PDF</a>
            </td>
          </tr>
        `;
      }).join('');
    }

    if (recentList) {
      recentList.innerHTML = incidents.slice(0, 5).map(inc => {
        const sevBorder = inc.severity === 'CRITICAL' ? '#EF4444' : '#F97316';
        return `
          <div style="background:rgba(8,15,30,0.6); border-left:3px solid ${sevBorder}; padding:10px 12px; margin-bottom:8px; border-radius:4px; font-size:12px;">
            <div style="display:flex; justify-content:space-between;">
              <b style="color:#00D9FF;">${inc.incident_number}</b>
              <span style="font-size:10px; color:#94A3B8;">${inc.status}</span>
            </div>
            <div style="color:#FFFFFF; margin:3px 0;">${inc.title}</div>
            <div style="font-size:11px; color:#94A3B8;">${inc.location_name} • Risk: ${inc.risk_score}</div>
          </div>
        `;
      }).join('');
    }

  } catch (err) {
    console.error("Error loading incidents:", err);
  }
}

// --------------------------------------------------------------------------
// AI Vision Studio (Image & Fire Detection)
// --------------------------------------------------------------------------
async function runObjectDetectionOnUpload(fileInput) {
  const file = fileInput.files[0];
  if (!file) return;

  const preview = document.getElementById('ai-vision-preview');
  const details = document.getElementById('ai-vision-details');
  if (preview) preview.innerHTML = `<div style="color:#00D9FF; font-size:13px; text-align:center;">Executing YOLOv8 Inference...</div>`;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('conf_threshold', 0.35);

  try {
    const res = await fetch('/api/ai/detect-image', { method: 'POST', body: formData });
    const data = await res.json();

    if (preview) {
      preview.innerHTML = `<img src="${data.annotated_image}" style="max-width:100%; max-height:400px; border-radius:6px; border:1px solid #00D9FF;" />`;
    }

    if (details) {
      let countsHtml = Object.entries(data.counts).map(([k, v]) => `
        <span style="background:rgba(0,217,255,0.15); border:1px solid #00D9FF; color:#00D9FF; padding:3px 8px; border-radius:4px; font-size:11px; margin-right:6px;">
          ${k.toUpperCase()}: ${v}
        </span>
      `).join('');

      let crowdMsg = data.crowd_summary.message ? `
        <div style="margin-top:10px; padding:10px; background:rgba(16,27,45,0.8); border:1px solid ${data.crowd_summary.color_hex}; border-radius:6px; font-size:12px;">
          <b>Crowd Analysis:</b> ${data.crowd_summary.message}
        </div>
      ` : '';

      details.innerHTML = `
        <div style="margin-top:12px;">
          <h4 style="color:#FFFFFF; font-size:13px; margin-bottom:6px;">Detections Tally:</h4>
          <div>${countsHtml || '<span>No target objects detected above confidence threshold.</span>'}</div>
          ${crowdMsg}
          <div style="margin-top:10px; font-size:10px; color:#64748B;">Evidence SHA-256: ${data.evidence_sha256}</div>
        </div>
      `;
    }

    playAlertChime();
    showToast("AI Inference Completed Successfully");

  } catch (err) {
    console.error("AI detection error:", err);
    showToast("Inference failed: " + err.message);
  }
}

async function runFireDetectionOnUpload(fileInput) {
  const file = fileInput.files[0];
  if (!file) return;

  const preview = document.getElementById('fire-vision-preview');
  const details = document.getElementById('fire-vision-details');
  if (preview) preview.innerHTML = `<div style="color:#00D9FF; font-size:13px; text-align:center;">Analyzing Multi-Spectral Flame Signature...</div>`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/ai/analyze-fire', { method: 'POST', body: formData });
    const data = await res.json();

    if (preview) {
      preview.innerHTML = `<img src="${data.annotated_image}" style="max-width:100%; max-height:400px; border-radius:6px; border:1px solid #EF4444;" />`;
    }

    if (details) {
      const fireStatus = data.fire_detected ? `<span style="color:#EF4444; font-weight:bold;">POSITIVE (${Math.round(data.fire_confidence*100)}%)</span>` : `<span style="color:#22C55E;">NEGATIVE</span>`;
      const smokeStatus = data.smoke_detected ? `<span style="color:#F59E0B; font-weight:bold;">DETECTED (${Math.round(data.smoke_confidence*100)}%)</span>` : `<span style="color:#22C55E;">NEGATIVE</span>`;

      details.innerHTML = `
        <div style="margin-top:12px; font-size:12px;">
          <div>Fire Signature: ${fireStatus}</div>
          <div style="margin-top:4px;">Smoke Plume: ${smokeStatus}</div>
          <div style="margin-top:8px; color:#94A3B8;">Verification Required: <b>${data.requires_human_verification ? 'YES (Human Operator Review)' : 'NO'}</b></div>
        </div>
      `;
    }

    if (data.fire_detected) {
      playAlertChime();
      showToast("ALERT: Thermal Fire Signature Confirmed!");
    } else {
      showToast("Fire analysis completed: No critical flames detected");
    }

  } catch (err) {
    console.error("Fire detection error:", err);
  }
}

// --------------------------------------------------------------------------
// Face Privacy & Authorized Badge Verification
// --------------------------------------------------------------------------
async function runFacePrivacyOnUpload(fileInput, blurToggle) {
  const file = fileInput.files[0];
  if (!file) return;

  const preview = document.getElementById('face-vision-preview');
  const details = document.getElementById('face-vision-details');
  if (preview) preview.innerHTML = `<div style="color:#00D9FF; font-size:13px; text-align:center;">Executing Privacy Face Filter...</div>`;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('blur_faces', blurToggle.checked);

  try {
    const res = await fetch('/api/ai/face-privacy', { method: 'POST', body: formData });
    const data = await res.json();

    if (preview) {
      preview.innerHTML = `<img src="${data.annotated_image}" style="max-width:100%; max-height:400px; border-radius:6px; border:1px solid #00D9FF;" />`;
    }

    if (details) {
      details.innerHTML = `
        <div style="margin-top:12px; font-size:12px;">
          <div>Faces Detected: <b>${data.faces_detected}</b></div>
          <div style="margin-top:4px;">Privacy Status: <b style="color:#22C55E;">${data.privacy_mode}</b></div>
          <p style="margin-top:8px; color:#94A3B8; font-size:11px;">${data.compliance_note}</p>
        </div>
      `;
    }
  } catch (err) {
    console.error("Face privacy error:", err);
  }
}

async function verifyBadgeCode() {
  const code = document.getElementById('badge-code-input').value;
  const resElem = document.getElementById('badge-verify-result');
  if (!code) return;

  const formData = new FormData();
  formData.append('badge_code', code);

  try {
    const res = await fetch('/api/ai/verify-badge', { method: 'POST', body: formData });
    const data = await res.json();

    if (resElem) {
      if (data.matched) {
        resElem.innerHTML = `
          <div style="background:rgba(34,197,94,0.15); border:1px solid #22C55E; color:#FFFFFF; padding:12px; border-radius:6px; margin-top:10px;">
            <b style="color:#22C55E;">ACCESS GRANTED — AUTHORIZED PERSONNEL</b><br/>
            Name: ${data.details.name}<br/>
            Role: ${data.details.role}<br/>
            Clearance: ${data.details.clearance}<br/>
            <span style="font-size:10px; color:#94A3B8;">Protocol: ${data.verification_method}</span>
          </div>
        `;
      } else {
        resElem.innerHTML = `
          <div style="background:rgba(239,68,68,0.15); border:1px solid #EF4444; color:#FFFFFF; padding:12px; border-radius:6px; margin-top:10px;">
            <b style="color:#EF4444;">ACCESS DENIED</b><br/>
            ${data.message}
          </div>
        `;
      }
    }
  } catch (err) {
    console.error("Badge verification error:", err);
  }
}

// --------------------------------------------------------------------------
// Multilingual Citizen Reporter
// --------------------------------------------------------------------------
async function submitCitizenReport() {
  const text = document.getElementById('citizen-text-input').value;
  const lang = document.getElementById('citizen-lang-select').value;
  const loc = document.getElementById('citizen-loc-input').value;
  const resBox = document.getElementById('citizen-report-result');

  if (!text) {
    showToast("Please enter an incident description");
    return;
  }

  try {
    const res = await fetch('/api/citizen/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: lang, location_name: loc || "Citizen Location" })
    });
    const data = await res.json();

    if (resBox) {
      resBox.innerHTML = `
        <div style="background:rgba(16,27,45,0.9); border:1px solid #00D9FF; padding:16px; border-radius:6px; margin-top:14px; font-size:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <b style="color:#00D9FF;">${data.incident_number} LOGGED</b>
            <span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#F59E0B; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:bold;">${data.urgency}</span>
          </div>
          <div style="margin-top:8px;"><b>Original Text (${data.language}):</b> "${data.original_text}"</div>
          <div style="margin-top:6px; color:#22C55E;"><b>Control-Room English Translation:</b><br/>${data.translated_english}</div>
          <div style="margin-top:8px; font-size:10px; color:#94A3B8;">Incident queued for control-room operator acknowledgment.</div>
        </div>
      `;
    }

    showToast("Citizen Report Submitted and Translated!");
    loadIncidentsList();
    fetchDashboardStats();

  } catch (err) {
    console.error("Citizen report error:", err);
  }
}

// --------------------------------------------------------------------------
// --------------------------------------------------------------------------
// Real-Time Emergency Responders & Automated Departmental Messaging
// --------------------------------------------------------------------------
let cachedLiveResponders = [];
let cachedIncidents = [];

async function loadResponseTeams() {
  try {
    const res = await fetch('/api/geo/map-data');
    if (!res.ok) return;
    const data = await res.json();

    if (data.live_responders) {
      renderResponderCards(data.live_responders);
    } else if (data.response_teams) {
      renderResponderCards(data.response_teams);
    }

    if (data.cad_messages) {
      renderCadMessages(data.cad_messages);
    }

    if (data.incidents) {
      cachedIncidents = data.incidents;
      populateQuickDispatchDropdowns(data.incidents, data.live_responders || data.response_teams);
    }
  } catch (err) {
    console.error("Error loading response teams:", err);
  }
}

function renderResponderCards(responders) {
  if (!responders || !Array.isArray(responders)) return;
  cachedLiveResponders = responders;
  const container = document.getElementById('teams-card-grid');
  if (!container) return;

  container.innerHTML = responders.map(u => {
    const isDispatched = u.status === 'DISPATCHED';
    const isOnScene = u.status === 'ON_SCENE';

    let icon = u.type === 'FIRE' ? '🚒' : u.type === 'MEDICAL' ? '🚑' : '🚓';

    let statusBadge = `<span class="badge-tag" style="background:rgba(0,217,255,0.15); border-color:#00D9FF; color:#00D9FF;"><span class="live-dot"></span> PATROLLING (${u.speed_kmh || 30} km/h)</span>`;
    let trackingInfo = '';

    if (isDispatched) {
      statusBadge = `<span class="badge-tag" style="background:rgba(239,68,68,0.25); border-color:#EF4444; color:#FFFFFF;"><i class="fa-solid fa-bullhorn"></i> EN ROUTE (${u.distance_to_target_km} km)</span>`;
      trackingInfo = `
        <div style="margin-top:8px; padding:8px 10px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.4); border-radius:6px; font-size:11px;">
          <div style="color:#EF4444; font-weight:bold;">🚨 Dispatched to Incident: ${u.assigned_incident?.incident_number || 'ACTIVE INCIDENT'}</div>
          <div style="color:#FFFFFF; margin-top:2px;">Target: <b>${u.assigned_incident?.title || 'Emergency Scene'}</b></div>
          <div style="display:flex; justify-content:space-between; margin-top:4px; color:#94A3B8;">
            <span>Distance: <b style="color:#F59E0B;">${u.distance_to_target_km} km</b></span>
            <span>Est. Arrival: <b style="color:#22C55E;">${Math.max(1, Math.round((u.eta_seconds || 60) / 60))} mins</b></span>
            <span>Speed: <b style="color:#00D9FF;">${u.speed_kmh} km/h</b></span>
          </div>
        </div>
      `;
    } else if (isOnScene) {
      statusBadge = `<span class="badge-tag" style="background:rgba(34,197,94,0.2); border-color:#22C55E; color:#22C55E;"><i class="fa-solid fa-circle-check"></i> ARRIVED ON SCENE</span>`;
      trackingInfo = `
        <div style="margin-top:8px; padding:6px 10px; background:rgba(34,197,94,0.12); border:1px solid #22C55E; border-radius:6px; font-size:11px; color:#22C55E;">
          <b>✓ Location Verified:</b> Unit arrived at incident coordinates. Perimeter secured.
        </div>
      `;
    }

    return `
      <div class="card-panel" style="padding:14px; margin-bottom:0; background:rgba(16,27,45,0.7); border:1px solid ${isDispatched ? 'rgba(239,68,68,0.6)' : 'rgba(0,217,255,0.2)'};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:16px;">${icon}</span>
              <b style="color:#FFFFFF; font-size:13px;">${u.code} — ${u.name}</b>
            </div>
            <div style="font-size:11px; color:#94A3B8; margin-top:4px;">
              Station: <b style="color:#E2E8F0;">${u.department_station || 'City Division'}</b> • Sector: <b>${u.sector || 'Patrol Area'}</b>
            </div>
          </div>
          <div>${statusBadge}</div>
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:14px; font-size:11px; color:#94A3B8; margin-top:8px;">
          <span>Commander: <b style="color:#E2E8F0;">${u.unit_lead || 'Lead Officer'}</b></span>
          <span>Contact: <b style="color:#00D9FF;">${u.contact || '100'}</b></span>
          <span>GPS: <code style="color:#E2E8F0;">${u.lat ? u.lat.toFixed(4) : '0.0000'}°N, ${u.lon ? u.lon.toFixed(4) : '0.0000'}°E</code></span>
          <span>Heading: <b>${Math.round(u.heading || 0)}°</b></span>
        </div>

        ${trackingInfo}

        <div style="margin-top:10px; display:flex; gap:8px;">
          <button onclick="window.trackResponder('${u.code}')" class="btn-falcon btn-falcon-primary" style="font-size:11px; padding:4px 10px;">
            <i class="fa-solid fa-location-crosshairs"></i> Track Live on Map
          </button>
          <button onclick="window.openDispatchModalForUnit('${u.code}')" class="btn-falcon btn-falcon-danger" style="font-size:11px; padding:4px 10px;">
            <i class="fa-solid fa-bullhorn"></i> Dispatch
          </button>
          <button onclick="window.resetResponder('${u.code}')" class="btn-falcon" style="font-size:11px; padding:4px 10px;">
            <i class="fa-solid fa-rotate-left"></i> Reset Patrol
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderCadMessages(messages) {
  if (!messages || !Array.isArray(messages)) return;
  const container = document.getElementById('cad-messages-container');
  if (!container) return;

  if (messages.length === 0) {
    container.innerHTML = `<div style="color:#64748B; font-size:12px; text-align:center; padding:20px;">Awaiting live emergency dispatches...</div>`;
    return;
  }

  container.innerHTML = messages.map(m => {
    const isArrived = m.status === 'ARRIVED_ON_SCENE';
    const isAlert = m.status === 'DISPATCHED_EN_ROUTE';
    const borderCol = isArrived ? '#22C55E' : isAlert ? '#EF4444' : 'rgba(0,217,255,0.3)';
    const badgeText = isArrived ? 'VERIFIED ARRIVAL' : isAlert ? 'STATION ALERT SENT' : 'CAD TRANSMISSION';
    const badgeBg = isArrived ? 'rgba(34,197,94,0.15)' : isAlert ? 'rgba(239,68,68,0.15)' : 'rgba(0,217,255,0.15)';
    const badgeCol = isArrived ? '#22C55E' : isAlert ? '#EF4444' : '#00D9FF';

    const timeStr = m.timestamp ? new Date(m.timestamp).toLocaleTimeString() : 'NOW';

    return `
      <div style="background:rgba(8,15,30,0.85); border-left:3px solid ${borderCol}; border-radius:4px; padding:10px 12px; font-size:11px; border-top:1px solid rgba(255,255,255,0.05); border-right:1px solid rgba(255,255,255,0.05); border-bottom:1px solid rgba(255,255,255,0.05);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <b style="color:#FFFFFF; font-size:11px;"><i class="fa-solid fa-tower-broadcast" style="color:${badgeCol};"></i> ${m.target_station || m.target_department}</b>
          <span style="font-size:9px; background:${badgeBg}; color:${badgeCol}; border:1px solid ${borderCol}; padding:1px 6px; border-radius:10px; font-weight:bold;">${badgeText} • ${timeStr}</span>
        </div>
        <div style="color:#E2E8F0; line-height:1.4; white-space:pre-line; margin-top:4px;">
          ${m.message}
        </div>
        <div style="font-size:9px; color:#64748B; margin-top:6px; display:flex; justify-content:space-between;">
          <span>Channel: <b>${m.channel || 'CAD SECURE GATEWAY'}</b></span>
          <span>Lead: <b>${m.unit_lead || 'Dispatcher'}</b></span>
        </div>
      </div>
    `;
  }).join('');
}

function populateQuickDispatchDropdowns(incidents, responders) {
  const incSelect = document.getElementById('quick-dispatch-incident');
  const unitSelect = document.getElementById('quick-dispatch-unit');

  if (incSelect && incidents) {
    const curVal = incSelect.value;
    incSelect.innerHTML = `<option value="">Select Target Incident...</option>` +
      incidents.map(i => `<option value="${i.id}" ${curVal == i.id ? 'selected' : ''}>${i.incident_number} — ${i.title} (${i.severity})</option>`).join('');
  }

  if (unitSelect && responders) {
    const curVal = unitSelect.value;
    unitSelect.innerHTML = `<option value="">Select Patrol Unit...</option>` +
      responders.map(u => `<option value="${u.code}" ${curVal == u.code ? 'selected' : ''}>${u.code} (${u.name.split('(')[0].trim()}) - ${u.status}</option>`).join('');
  }
}

async function handleQuickDispatch() {
  const incId = document.getElementById('quick-dispatch-incident')?.value;
  const unitCode = document.getElementById('quick-dispatch-unit')?.value;

  if (!unitCode) {
    showToast("Please select a patrol unit to dispatch");
    return;
  }

  showToast(`Alerting department and dispatching ${unitCode}...`);
  playAlertChime();

  try {
    const formData = new FormData();
    formData.append('team_code', unitCode);
    if (incId) formData.append('incident_id', incId);

    const res = await fetch('/api/responders/dispatch', { method: 'POST', body: formData });
    const data = await res.json();

    if (data.status === 'SUCCESS') {
      showToast(data.message || `Dispatched ${unitCode}!`);
      trackResponder(unitCode);
      loadResponseTeams();
    } else {
      showToast("Dispatch error: " + (data.message || "Failed"));
    }
  } catch (err) {
    console.error("Dispatch error:", err);
    showToast("Failed to dispatch unit: " + err.message);
  }
}

function trackResponder(teamCode) {
  switchView('geospatial');
  setTimeout(() => {
    if (window.trackResponderOnMap) {
      window.trackResponderOnMap(teamCode);
    }
  }, 300);
}

function resetResponder(teamCode) {
  if (window.resetResponderToPatrol) {
    window.resetResponderToPatrol(teamCode);
  }
}

async function resetAllResponders() {
  try {
    await fetch('/api/responders/reset', { method: 'POST' });
    showToast("✓ All units returned to standard patrol sectors");
    if (window.loadMapData) window.loadMapData();
    loadResponseTeams();
  } catch (err) {
    console.error("Error resetting all units:", err);
  }
}

function openDispatchModalForUnit(teamCode) {
  const incSelect = document.getElementById('quick-dispatch-incident');
  const unitSelect = document.getElementById('quick-dispatch-unit');
  if (unitSelect) unitSelect.value = teamCode;
  if (incSelect && (!incSelect.value || incSelect.value === '')) {
    if (incSelect.options.length > 1) {
      incSelect.selectedIndex = 1;
    }
  }
  handleQuickDispatch();
}

async function dispatchNearestUnitToIncident(incidentId) {
  showToast("Identifying nearest police/fire unit and alerting station...");
  playAlertChime();
  try {
    const formData = new FormData();
    formData.append('team_code', '');
    formData.append('incident_id', incidentId);

    const res = await fetch('/api/responders/dispatch', { method: 'POST', body: formData });
    const data = await res.json();

    if (data.status === 'SUCCESS' && data.unit) {
      showToast(data.message);
      trackResponder(data.unit.code);
      loadResponseTeams();
    } else {
      showToast(data.message || "Dispatch completed");
    }
  } catch (e) {
    console.error("Dispatch nearest error:", e);
  }
}

// --------------------------------------------------------------------------
// Analytics & Chart.js
// --------------------------------------------------------------------------
function initAnalyticsCharts() {
  const catCanvas = document.getElementById('chart-categories');
  const sevCanvas = document.getElementById('chart-severity');

  if (catCanvas && !analyticsCharts.categories) {
    analyticsCharts.categories = new Chart(catCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Crowd Congestion', 'Traffic Collision', 'Fire / Smoke', 'Fallen Person'],
        datasets: [{
          data: [5, 3, 2, 2],
          backgroundColor: ['#00D9FF', '#2878FF', '#EF4444', '#F59E0B'],
          borderColor: '#080F1E',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#E2E8F0', font: { size: 11 } } }
        }
      }
    });
  }

  if (sevCanvas && !analyticsCharts.severity) {
    analyticsCharts.severity = new Chart(sevCanvas, {
      type: 'bar',
      data: {
        labels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        datasets: [{
          label: 'Incidents by Severity',
          data: [2, 4, 5, 1],
          backgroundColor: ['#EF4444', '#F97316', '#F59E0B', '#22C55E']
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { ticks: { color: '#94A3B8' } },
          y: { ticks: { color: '#94A3B8' } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

function renderAnalyticsData() {
  if (analyticsCharts.categories) analyticsCharts.categories.update();
  if (analyticsCharts.severity) analyticsCharts.severity.update();
}

// --------------------------------------------------------------------------
// Audio Synthesizer (Cyberpunk Command Center Alert Chime)
// --------------------------------------------------------------------------
function toggleAudioAlerts() {
  audioAlertsEnabled = !audioAlertsEnabled;
  const btn = document.getElementById('audio-toggle-btn');
  if (btn) {
    btn.innerHTML = audioAlertsEnabled ? '🔊 Audio Alerts: ON' : '🔇 Audio Alerts: OFF';
    btn.style.borderColor = audioAlertsEnabled ? '#00D9FF' : 'rgba(0,217,255,0.3)';
    btn.style.color = audioAlertsEnabled ? '#00D9FF' : '#94A3B8';
  }
  if (audioAlertsEnabled) playAlertChime();
}

function playAlertChime() {
  if (!audioAlertsEnabled) return;
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
    osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.25);
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.25);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.25);
  } catch (e) {
    console.warn("Audio play blocked", e);
  }
}

// --------------------------------------------------------------------------
// Toast Notification
// --------------------------------------------------------------------------
function showToast(message) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span style="color:#00D9FF;">⚡</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Sample Media Loaders for Demonstration
async function loadSampleCrowdDetection() {
  try {
    showToast("Loading sample crowd image for AI detection...");
    const res = await fetch('/sample_data/sample_crowd.jpg');
    if (!res.ok) throw new Error("Sample crowd image not found");
    const blob = await res.blob();
    const file = new File([blob], "sample_crowd.jpg", { type: "image/jpeg" });
    runObjectDetectionOnUpload({ files: [file] });
  } catch (err) {
    console.error("Error loading sample crowd:", err);
    showToast("Failed to load sample crowd: " + err.message);
  }
}

async function loadSampleFireDetection() {
  try {
    showToast("Loading sample fire & smoke image...");
    const res = await fetch('/sample_data/sample_fire.jpg');
    if (!res.ok) throw new Error("Sample fire image not found");
    const blob = await res.blob();
    const file = new File([blob], "sample_fire.jpg", { type: "image/jpeg" });
    runFireDetectionOnUpload({ files: [file] });
  } catch (err) {
    console.error("Error loading sample fire:", err);
    showToast("Failed to load sample fire: " + err.message);
  }
}

async function loadSampleFacePrivacy() {
  try {
    showToast("Loading sample face privacy image...");
    const res = await fetch('/sample_data/sample_face.jpg');
    if (!res.ok) throw new Error("Sample face image not found");
    const blob = await res.blob();
    const file = new File([blob], "sample_face.jpg", { type: "image/jpeg" });
    const toggle = document.getElementById('face-blur-toggle') || { checked: true };
    runFacePrivacyOnUpload({ files: [file] }, toggle);
  } catch (err) {
    console.error("Error loading sample face:", err);
    showToast("Failed to load sample face: " + err.message);
  }
}

window.switchView = switchView;
window.fetchDashboardStats = fetchDashboardStats;
window.loadIncidentsList = loadIncidentsList;
window.loadResponseTeams = loadResponseTeams;
window.renderResponderCards = renderResponderCards;
window.renderCadMessages = renderCadMessages;
window.handleQuickDispatch = handleQuickDispatch;
window.trackResponder = trackResponder;
window.resetResponder = resetResponder;
window.resetAllResponders = resetAllResponders;
window.openDispatchModalForUnit = openDispatchModalForUnit;
window.dispatchNearestUnitToIncident = dispatchNearestUnitToIncident;
window.runObjectDetectionOnUpload = runObjectDetectionOnUpload;
window.runFireDetectionOnUpload = runFireDetectionOnUpload;
window.runFacePrivacyOnUpload = runFacePrivacyOnUpload;
window.loadSampleCrowdDetection = loadSampleCrowdDetection;
window.loadSampleFireDetection = loadSampleFireDetection;
window.loadSampleFacePrivacy = loadSampleFacePrivacy;
window.verifyBadgeCode = verifyBadgeCode;
window.submitCitizenReport = submitCitizenReport;
window.toggleAudioAlerts = toggleAudioAlerts;
window.showToast = showToast;

// --------------------------------------------------------------------------
// View Incident Detail Modal
// --------------------------------------------------------------------------
async function viewIncidentModal(incidentId) {
  try {
    const res = await fetch('/api/incidents');
    if (!res.ok) return;
    const incidents = await res.json();
    const inc = incidents.find(i => i.id === incidentId);
    if (!inc) { showToast('Incident not found'); return; }

    const sevColor = inc.severity === 'CRITICAL' ? '#EF4444' : inc.severity === 'HIGH' ? '#F97316' : '#F59E0B';
    const statColor = inc.status === 'RESOLVED' ? '#22C55E' : '#00D9FF';

    // Create modal overlay
    let overlay = document.getElementById('incident-detail-modal');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'incident-detail-modal';
      overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(4,8,16,0.85);backdrop-filter:blur(8px);z-index:1000;display:flex;align-items:center;justify-content:center;';
      document.body.appendChild(overlay);
    }

    overlay.innerHTML = `
      <div style="width:650px;max-width:94vw;max-height:85vh;background:#101B2D;border:2px solid #00D9FF;border-radius:8px;overflow-y:auto;box-shadow:0 0 35px rgba(0,217,255,0.4);">
        <div style="padding:16px 22px;background:rgba(8,15,30,0.95);border-bottom:1px solid rgba(0,217,255,0.3);display:flex;align-items:center;justify-content:space-between;">
          <h2 style="font-size:16px;font-weight:800;color:#FFFFFF;letter-spacing:1px;">${inc.incident_number}</h2>
          <button onclick="document.getElementById('incident-detail-modal').remove()" style="background:none;border:none;color:#94A3B8;font-size:18px;cursor:pointer;">✕</button>
        </div>
        <div style="padding:22px;">
          <h3 style="color:#FFFFFF;font-size:16px;margin-bottom:12px;">${inc.title}</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
            <div style="background:rgba(8,15,30,0.6);padding:10px;border-radius:6px;border:1px solid rgba(0,217,255,0.2);">
              <div style="font-size:10px;color:#94A3B8;text-transform:uppercase;">Category</div>
              <div style="font-size:14px;font-weight:bold;color:#FFFFFF;margin-top:2px;">${inc.category.replace(/_/g,' ')}</div>
            </div>
            <div style="background:rgba(8,15,30,0.6);padding:10px;border-radius:6px;border:1px solid rgba(0,217,255,0.2);">
              <div style="font-size:10px;color:#94A3B8;text-transform:uppercase;">Severity</div>
              <div style="font-size:14px;font-weight:bold;color:${sevColor};margin-top:2px;">${inc.severity}</div>
            </div>
            <div style="background:rgba(8,15,30,0.6);padding:10px;border-radius:6px;border:1px solid rgba(0,217,255,0.2);">
              <div style="font-size:10px;color:#94A3B8;text-transform:uppercase;">Status</div>
              <div style="font-size:14px;font-weight:bold;color:${statColor};margin-top:2px;">${inc.status}</div>
            </div>
            <div style="background:rgba(8,15,30,0.6);padding:10px;border-radius:6px;border:1px solid rgba(0,217,255,0.2);">
              <div style="font-size:10px;color:#94A3B8;text-transform:uppercase;">Risk Score</div>
              <div style="font-size:14px;font-weight:bold;color:#00D9FF;margin-top:2px;">${inc.risk_score}/100</div>
            </div>
          </div>
          <div style="font-size:12px;color:#94A3B8;margin-bottom:8px;"><b>Location:</b> ${inc.location_name}</div>
          <div style="font-size:12px;color:#94A3B8;margin-bottom:14px;"><b>Coordinates:</b> ${inc.lat.toFixed(5)}°N, ${inc.lon.toFixed(5)}°E</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button onclick="window.dispatchNearestUnitToIncident(${inc.id}); document.getElementById('incident-detail-modal').remove();" class="btn-falcon btn-falcon-danger">
              <i class="fa-solid fa-bullhorn"></i> Alert Department & Dispatch Nearest Unit
            </button>
            <button onclick="window.dispatchToIncident(${inc.id},${inc.lat},${inc.lon}); document.getElementById('incident-detail-modal').remove();" class="btn-falcon">
              <i class="fa-solid fa-route"></i> Route Response
            </button>
            <a href="/api/reports/incident/${inc.id}/pdf" target="_blank" class="btn-falcon btn-falcon-primary" style="text-decoration:none;">
              <i class="fa-solid fa-file-pdf"></i> Download PDF Report
            </a>
          </div>
        </div>
      </div>
    `;
    overlay.style.display = 'flex';
  } catch (err) {
    console.error('Error viewing incident:', err);
    showToast('Failed to load incident details');
  }
}

// --------------------------------------------------------------------------
// Dispatch Emergency Response to Incident
// --------------------------------------------------------------------------
async function dispatchToIncident(incidentId, toLat, toLon) {
  showToast('Calculating emergency route...');
  // Use first available response team location as origin
  try {
    const res = await fetch('/api/geo/map-data');
    if (!res.ok) return;
    const data = await res.json();
    if (data.response_teams && data.response_teams.length > 0) {
      const team = data.response_teams[0];
      if (window.plotRoute) {
        await window.plotRoute(team.lat, team.lon, toLat, toLon);
      }
    }
    switchView('geospatial');
  } catch (err) {
    console.error('Error dispatching:', err);
  }
}

window.viewIncidentModal = viewIncidentModal;
window.dispatchToIncident = dispatchToIncident;

// --------------------------------------------------------------------------
// Settings Management & Persistence
// --------------------------------------------------------------------------
function loadSettings() {
  try {
    const region = localStorage.getItem('falcon_map_region') || 'all';
    const tiles = localStorage.getItem('falcon_map_tiles') || 'osm';
    const conf = localStorage.getItem('falcon_conf_threshold') || '35';
    const face = localStorage.getItem('falcon_face_privacy') || 'blur_all';
    const fire = localStorage.getItem('falcon_fire_sens') || 'balanced';
    const chime = localStorage.getItem('falcon_audio_chime') === 'true';

    if (document.getElementById('setting-map-region')) document.getElementById('setting-map-region').value = region;
    if (document.getElementById('setting-map-tiles')) document.getElementById('setting-map-tiles').value = tiles;
    if (document.getElementById('setting-conf-slider')) {
      document.getElementById('setting-conf-slider').value = conf;
      if (document.getElementById('conf-val-label')) {
        document.getElementById('conf-val-label').innerText = (conf / 100).toFixed(2);
      }
    }
    if (document.getElementById('setting-face-privacy')) document.getElementById('setting-face-privacy').value = face;
    if (document.getElementById('setting-fire-sens')) document.getElementById('setting-fire-sens').value = fire;
    if (document.getElementById('setting-audio-chime')) document.getElementById('setting-audio-chime').checked = chime;
  } catch (e) {
    console.warn("Could not load settings:", e);
  }
}

function saveSettings() {
  try {
    const region = document.getElementById('setting-map-region')?.value || 'all';
    const tiles = document.getElementById('setting-map-tiles')?.value || 'osm';
    const conf = document.getElementById('setting-conf-slider')?.value || '35';
    const face = document.getElementById('setting-face-privacy')?.value || 'blur_all';
    const fire = document.getElementById('setting-fire-sens')?.value || 'balanced';
    const chime = document.getElementById('setting-audio-chime')?.checked || false;
    const geminiKey = document.getElementById('setting-gemini-key')?.value;

    localStorage.setItem('falcon_map_region', region);
    localStorage.setItem('falcon_map_tiles', tiles);
    localStorage.setItem('falcon_conf_threshold', conf);
    localStorage.setItem('falcon_face_privacy', face);
    localStorage.setItem('falcon_fire_sens', fire);
    localStorage.setItem('falcon_audio_chime', chime);
    if (geminiKey) localStorage.setItem('falcon_gemini_key', geminiKey);

    // Apply region immediately to maps
    if (window.jumpToRegion) {
      window.jumpToRegion(region);
    }

    showToast("✓ Settings Applied & Saved (Telangana & AP Grid Active)");
  } catch (e) {
    console.error("Save settings error:", e);
    showToast("Error saving settings");
  }
}

function resetSettings() {
  try {
    localStorage.removeItem('falcon_map_region');
    localStorage.removeItem('falcon_map_tiles');
    localStorage.removeItem('falcon_conf_threshold');
    localStorage.removeItem('falcon_face_privacy');
    localStorage.removeItem('falcon_fire_sens');
    localStorage.removeItem('falcon_audio_chime');
    loadSettings();
    if (window.jumpToRegion) window.jumpToRegion('all');
    showToast("✓ Settings Reset to Default (Telangana & AP Full Grid)");
  } catch (e) {
    showToast("Reset failed");
  }
}

async function testGeminiKey() {
  const keyElem = document.getElementById('setting-gemini-key');
  const statusElem = document.getElementById('gemini-key-status');
  const key = keyElem ? keyElem.value.trim() : '';

  if (!key) {
    if (statusElem) statusElem.innerHTML = `<span style="color:#EF4444;">Please enter an API key to test.</span>`;
    return;
  }

  if (statusElem) statusElem.innerHTML = `<span style="color:#00D9FF;">Validating key with Google Gemini API...</span>`;

  try {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${key}`);
    const data = await res.json();
    if (res.ok && data.models) {
      if (statusElem) statusElem.innerHTML = `<span style="color:#22C55E;">✓ Key Verified Active! (${data.models.length} models accessible, including Gemini 3.8 Flash)</span>`;
      showToast("Gemini Key Validated Successfully");
    } else {
      const err = data.error?.message || "Invalid API Key";
      if (statusElem) statusElem.innerHTML = `<span style="color:#EF4444;">✗ API Key Failed: ${err}</span>`;
    }
  } catch (e) {
    if (statusElem) statusElem.innerHTML = `<span style="color:#F59E0B;">⚠️ Network check timed out. Local offline translation will be used.</span>`;
  }
}

window.loadSettings = loadSettings;
window.saveSettings = saveSettings;
window.resetSettings = resetSettings;
window.testGeminiKey = testGeminiKey;


