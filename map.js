/**
 * FALCON EYE — Geospatial GIS Leaflet Map Engine
 * Specialized Real-World Telangana & Andhra Pradesh Command Center Map.
 * Ultra-fast Google Maps Roadmap + Google Satellite Hybrid + OpenStreetMap + CartoDB Dark.
 * State-wide coverage: Hyderabad, Warangal, Karimnagar, Nizamabad,
 * Visakhapatnam, Vijayawada, Amaravati, Guntur, Tirupati, Kurnool.
 */

let commandMap = null;
let gisMap = null;
let routeLayer = null;
let droneMarker = null;
let responderMarkers = { command: {}, gis: {} };
let responderRouteLayer = null;
let activeTrackedUnitCode = null;

// Combined Geographic Center and Bounds of Telangana and Andhra Pradesh
const TG_AP_CENTER = [16.80, 80.00];
const TG_AP_ZOOM = 7;
const TG_AP_BOUNDS = [[13.2, 76.6], [19.9, 84.8]];

// Predefined Quick-Jump Region Coordinates across Telangana & Andhra Pradesh
const REGION_COORDINATES = {
  'all': { name: 'Telangana & Andhra Pradesh (Full View)', center: [16.80, 80.00], zoom: 7, bounds: TG_AP_BOUNDS },
  'tg': { name: 'Telangana State', center: [17.85, 79.10], zoom: 8 },
  'ap': { name: 'Andhra Pradesh State', center: [15.90, 80.50], zoom: 8 },
  'hyd': { name: 'Hyderabad Metro (Telangana)', center: [17.3850, 78.4867], zoom: 12 },
  'wgl': { name: 'Warangal Cultural Hub (Telangana)', center: [17.9784, 79.5941], zoom: 12 },
  'krm': { name: 'Karimnagar District (Telangana)', center: [18.4386, 79.1288], zoom: 12 },
  'vzg': { name: 'Visakhapatnam Coast (Andhra Pradesh)', center: [17.7126, 83.3241], zoom: 12 },
  'bza': { name: 'Vijayawada / Amaravati (Andhra Pradesh)', center: [16.5062, 80.6480], zoom: 12 },
  'gnt': { name: 'Guntur District (Andhra Pradesh)', center: [16.3067, 80.4365], zoom: 12 },
  'tpt': { name: 'Tirupati Security Zone (Andhra Pradesh)', center: [13.6369, 79.4042], zoom: 13 },
  'knl': { name: 'Kurnool Gateway (Andhra Pradesh)', center: [15.8281, 78.0373], zoom: 12 }
};

function initMaps() {
  if (typeof L === 'undefined') {
    console.warn("[Falcon Eye] Leaflet loading, retrying in 100ms...");
    setTimeout(initMaps, 100);
    return;
  }

  // Check user settings from localStorage if set
  let initialRegion = 'all';
  try {
    const savedRegion = localStorage.getItem('falcon_map_region');
    if (savedRegion && REGION_COORDINATES[savedRegion]) {
      initialRegion = savedRegion;
    }
  } catch (e) {}

  const initConfig = REGION_COORDINATES[initialRegion] || REGION_COORDINATES['all'];

  if (document.getElementById('command-map') && !commandMap) {
    commandMap = createLeafletMap('command-map', initConfig.center, initConfig.zoom);
    window.commandMap = commandMap;
    if (initialRegion === 'all') {
      commandMap.fitBounds(TG_AP_BOUNDS, { padding: [20, 20], maxZoom: 8 });
    }
  }
  if (document.getElementById('gis-map') && !gisMap) {
    gisMap = createLeafletMap('gis-map', initConfig.center, initConfig.zoom);
    window.gisMap = gisMap;
    if (initialRegion === 'all') {
      gisMap.fitBounds(TG_AP_BOUNDS, { padding: [20, 20], maxZoom: 8 });
    }
  }
  loadMapData();

  // Force layout recalculation after DOM paint
  setTimeout(() => {
    if (commandMap) {
      commandMap.invalidateSize(true);
      if (initialRegion === 'all') commandMap.fitBounds(TG_AP_BOUNDS, { padding: [20, 20], maxZoom: 8 });
    }
    if (gisMap) {
      gisMap.invalidateSize(true);
      if (initialRegion === 'all') gisMap.fitBounds(TG_AP_BOUNDS, { padding: [20, 20], maxZoom: 8 });
    }
  }, 350);
}

function ensureGisMap() {
  if (typeof L === 'undefined') return;
  const container = document.getElementById('gis-map');
  if (!container) return;

  if (!gisMap) {
    gisMap = createLeafletMap('gis-map', TG_AP_CENTER, TG_AP_ZOOM);
    window.gisMap = gisMap;
    gisMap.fitBounds(TG_AP_BOUNDS, { padding: [20, 20], maxZoom: 8 });
    loadMapData();
  }

  setTimeout(() => {
    if (gisMap) {
      gisMap.invalidateSize(true);
      gisMap.fitBounds(TG_AP_BOUNDS, { padding: [20, 20], maxZoom: 8 });
    }
  }, 100);
}

function createLeafletMap(elemId, centerCoords, zoomLevel) {
  const container = document.getElementById(elemId);
  if (!container) return null;

  const map = L.map(elemId, {
    center: centerCoords,
    zoom: zoomLevel,
    minZoom: 6,
    maxZoom: 19,
    maxBounds: [[11.0, 72.0], [22.5, 88.0]],
    maxBoundsViscosity: 0.8,
    zoomControl: true,
    attributionControl: false
  });

  // 1. Google Real Road Map (100% reliable, zero-blocking, detailed Telangana & Andhra Pradesh coverage)
  const googleRoads = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: 'Map © Google'
  });

  // 2. Google High-Resolution Satellite Hybrid (Real aerial photos with state highways and district labels)
  const googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: 'Imagery © Google'
  });

  // 3. OpenStreetMap (Standard community road map)
  const osmRealTiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    subdomains: ['a', 'b', 'c'],
    attribution: '© OpenStreetMap contributors'
  });

  // 4. CartoDB Dark Matter (Tactical cyber command view)
  const cartoDark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
    maxZoom: 19,
    subdomains: ['a', 'b', 'c', 'd']
  });

  // 5. Esri High-Resolution World Imagery
  const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles © Esri'
  });

  // Base map selection
  const baseMaps = {
    "🗺️ Real Road Map (Google Maps)": googleRoads,
    "🛰️ Real Satellite Imagery (Google)": googleHybrid,
    "🌍 OpenStreetMap Standard": osmRealTiles,
    "🌌 Tactical Dark Command": cartoDark,
    "📡 Esri Satellite Aerial": esriSatellite
  };

  // Determine user's preferred default tile style
  let preferredTiles = googleRoads;
  try {
    const savedStyle = localStorage.getItem('falcon_map_tiles');
    if (savedStyle === 'satellite') preferredTiles = googleHybrid;
    else if (savedStyle === 'osm') preferredTiles = osmRealTiles;
    else if (savedStyle === 'dark') preferredTiles = cartoDark;
    else preferredTiles = googleRoads;
  } catch (e) {}

  preferredTiles.addTo(map);

  // Add interactive Layer Switcher on Top-Right of map
  L.control.layers(baseMaps, null, { position: 'topright', collapsed: false }).addTo(map);

  return map;
}

// Custom Leaflet DivIcons for Futuristic HUD styling
function createPulsingMarker(colorHex) {
  return L.divIcon({
    className: 'custom-pulsing-icon',
    html: `
      <div style="position: relative; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 28px; height: 28px; border-radius: 50%; background: ${colorHex}; opacity: 0.4; animation: live-blink 1.5s infinite;"></div>
        <div style="position: absolute; width: 14px; height: 14px; border-radius: 50%; background: ${colorHex}; border: 2px solid #FFFFFF; box-shadow: 0 0 12px ${colorHex};"></div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
}

function createDroneIcon(heading) {
  return L.divIcon({
    className: 'drone-icon',
    html: `
      <div style="transform: rotate(${heading}deg); transition: transform 0.5s ease; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="#00D9FF" stroke="#FFFFFF" stroke-width="1.5" style="filter: drop-shadow(0 0 10px #00D9FF);">
          <polygon points="12 2 19 21 12 17 5 21 12 2"></polygon>
        </svg>
      </div>
    `,
    iconSize: [34, 34],
    iconAnchor: [17, 17]
  });
}

async function loadMapData() {
  try {
    const res = await fetch('/api/geo/map-data');
    if (!res.ok) return;
    const data = await res.json();

    [commandMap, gisMap].forEach(map => {
      if (!map) return;

      // Clear existing markers if any
      map.eachLayer(layer => {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
          map.removeLayer(layer);
        }
      });

      // 1. Incidents across Telangana & Andhra Pradesh
      if (data.incidents) {
        data.incidents.forEach(inc => {
          const sevColor = inc.severity === 'CRITICAL' ? '#EF4444' : inc.severity === 'HIGH' ? '#F97316' : '#F59E0B';
          const marker = L.marker([inc.lat, inc.lon], { icon: createPulsingMarker(sevColor) }).addTo(map);
          marker.bindPopup(`
            <div style="font-family: sans-serif; font-size: 12px; color: #101B2D; min-width: 220px;">
              <b style="color: ${sevColor}; font-size:13px;">${inc.incident_number}</b><br/>
              <b style="color: #080F1E; font-size:12px;">${inc.title}</b><br/>
              <div style="margin: 4px 0;">Category: <b>${inc.category.replace(/_/g, ' ')}</b></div>
              <div>Severity: <b style="color:${sevColor};">${inc.severity}</b></div>
              <div>Location: <b>${inc.location_name}</b></div>
              <div>Risk Score: <b style="color:#0088CC;">${inc.risk_score}/100</b></div>
              <div style="margin-top:8px; display:flex; gap:6px;">
                <button onclick="window.dispatchToIncident(${inc.id}, ${inc.lat}, ${inc.lon})" style="background:#080F1E; color:#00D9FF; border:1px solid #00D9FF; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold;">
                  🚨 Route Response
                </button>
                <button onclick="window.viewIncidentModal(${inc.id})" style="background:#101B2D; color:#FFFFFF; border:1px solid #94A3B8; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:11px;">
                  Details
                </button>
              </div>
            </div>
          `);
        });
      }

      // 2. Surveillance Cameras across Telangana & Andhra Pradesh
      if (data.cameras) {
        data.cameras.forEach(cam => {
          const camIcon = L.divIcon({
            className: 'camera-pin',
            html: `<div style="background:#080F1E; border:1px solid #00D9FF; color:#00D9FF; padding:3px 7px; border-radius:4px; font-size:10px; font-weight:bold; box-shadow:0 0 10px rgba(0,217,255,0.4); white-space:nowrap;">📹 ${cam.code}</div>`,
            iconSize: [85, 20]
          });
          L.marker([cam.lat, cam.lon], { icon: camIcon }).addTo(map)
            .bindPopup(`
              <div style="font-family:sans-serif; font-size:12px; color:#101B2D;">
                <b style="color:#0088CC;">${cam.code}</b><br/>
                <b>${cam.name}</b><br/>
                <span>Location: ${cam.zone}</span><br/>
                <span>Status: <b style="color:#22C55E;">● ONLINE</b></span>
              </div>
            `);
        });
      }

      // 3. Dynamic Police & Fire Responders across Telangana & Andhra Pradesh
      if (data.live_responders || data.response_teams) {
        updateMapResponders(data.live_responders || data.response_teams);
      }

      // 4. Emergency Hospitals & Fire Stations across Telangana & Andhra Pradesh
      if (data.facilities) {
        data.facilities.forEach(fac => {
          const isHosp = fac.type === 'HOSPITAL';
          const facIcon = L.divIcon({
            className: 'fac-pin',
            html: `<div style="background:#FFFFFF; border:2px solid ${isHosp?'#EF4444':'#F59E0B'}; color:#080F1E; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:bold; white-space:nowrap; box-shadow:0 0 8px rgba(0,0,0,0.4);">${isHosp?'🏥':'🚒'} ${fac.city || ''}</div>`,
            iconSize: [70, 20]
          });
          L.marker([fac.lat, fac.lon], { icon: facIcon }).addTo(map)
            .bindPopup(`
              <div style="font-family:sans-serif; font-size:12px; color:#101B2D;">
                <b style="color:${isHosp?'#EF4444':'#F59E0B'};">${fac.name}</b><br/>
                <span>Region: <b>${fac.city || ''}, ${fac.state || ''}</b></span><br/>
                <span>Type: <b>${fac.type}</b></span><br/>
                <span>Emergency Contact: <b>${fac.contact}</b></span>
              </div>
            `);
        });
      }

      // 5. UAV Drone Real-Time Position
      if (data.drone) {
        droneMarker = L.marker([data.drone.lat, data.drone.lon], { icon: createDroneIcon(data.drone.heading_deg) }).addTo(map);
        droneMarker.bindPopup(`
          <div style="font-family:sans-serif; font-size:12px; color:#101B2D;">
            <b style="color:#0088CC;">${data.drone.callsign} [UAV TELEMETRY]</b><br/>
            <span>Sector: <b>${data.drone.target_zone}</b></span><br/>
            <span>Status: <b>${data.drone.status}</b></span><br/>
            <span>Altitude: <b>${data.drone.altitude_m} m</b> | Speed: <b>${data.drone.speed_kmh} km/h</b></span><br/>
            <span>Battery Life: <b style="color:#22C55E;">${Math.round(data.drone.battery_pct)}%</b></span>
          </div>
        `);
      }
    });

  } catch (err) {
    console.error("Error fetching map data:", err);
  }
}

// Function to update drone position in real-time on map
function updateMapDrone(telemetry) {
  if (!telemetry || !droneMarker) return;
  droneMarker.setLatLng([telemetry.lat, telemetry.lon]);
  droneMarker.setIcon(createDroneIcon(telemetry.heading_deg));
}

// --------------------------------------------------------------------------
// Real-Time Dynamic Police & Fire Responders Map Layer
// --------------------------------------------------------------------------
function createResponderIcon(unit) {
  const isDispatched = unit.status === 'DISPATCHED';
  const isOnScene = unit.status === 'ON_SCENE';

  let emoji = '🚓';
  let bg = '#0A2540';
  let border = '#00D9FF';
  let animation = '';

  if (unit.type === 'FIRE') {
    emoji = '🚒';
    bg = '#7F1D1D';
    border = '#EF4444';
  } else if (unit.type === 'MEDICAL') {
    emoji = '🚑';
    bg = '#064E3B';
    border = '#22C55E';
  }

  let statusBadge = `<span style="font-size:8px; opacity:0.85; background:rgba(0,0,0,0.4); padding:1px 4px; border-radius:3px;">PATROL</span>`;
  if (isDispatched) {
    statusBadge = `<span style="font-size:8px; color:#FFFFFF; background:#DC2626; padding:1px 5px; border-radius:3px; font-weight:bold;">🚨 EN ROUTE (${unit.distance_to_target_km}km)</span>`;
    border = '#EF4444';
    animation = 'box-shadow: 0 0 14px #EF4444; border-color:#F59E0B;';
  } else if (isOnScene) {
    statusBadge = `<span style="font-size:8px; color:#FFFFFF; background:#16A34A; padding:1px 5px; border-radius:3px; font-weight:bold;">✓ ON SCENE</span>`;
    border = '#22C55E';
    animation = 'box-shadow: 0 0 12px #22C55E;';
  }

  const html = `
    <div style="background:${bg}; border:2px solid ${border}; color:#FFFFFF; padding:2px 7px; border-radius:12px; font-size:10px; font-weight:bold; white-space:nowrap; display:flex; align-items:center; gap:4px; ${animation}">
      <span>${emoji}</span>
      <span>${unit.code}</span>
      ${statusBadge}
    </div>
  `;

  return L.divIcon({
    className: 'responder-unit-pin',
    html: html,
    iconSize: [120, 24],
    iconAnchor: [60, 12]
  });
}

function renderResponderPopupContent(unit) {
  const isDisp = unit.status === 'DISPATCHED';
  const isOnScene = unit.status === 'ON_SCENE';
  const statColor = isDisp ? '#F59E0B' : isOnScene ? '#22C55E' : '#00D9FF';

  let incidentBlock = '';
  if (unit.assigned_incident) {
    incidentBlock = `
      <div style="margin-top:8px; padding:6px 8px; background:rgba(245,158,11,0.12); border:1px solid #F59E0B; border-radius:4px; font-size:11px;">
        <div style="color:#F59E0B; font-weight:bold;">🚨 DISPATCHED TO INCIDENT</div>
        <div><b>${unit.assigned_incident.incident_number}</b>: ${unit.assigned_incident.title}</div>
        <div style="margin-top:2px;">Location: <b>${unit.assigned_incident.location_name}</b></div>
        <div style="margin-top:2px;">Distance Remaining: <b style="color:#F59E0B;">${unit.distance_to_target_km} km</b></div>
        <div>Estimated Arrival: <b>${Math.max(1, Math.round(unit.eta_seconds / 60))} mins</b></div>
      </div>
    `;
  }

  return `
    <div style="font-family:sans-serif; font-size:12px; color:#101B2D; min-width:230px;">
      <div style="font-size:13px; font-weight:bold; color:#0A2540; margin-bottom:2px;">
        ${unit.type === 'FIRE' ? '🚒' : unit.type === 'MEDICAL' ? '🚑' : '🚓'} ${unit.name}
      </div>
      <div style="color:#64748B; font-size:11px; margin-bottom:4px;">${unit.department_station || unit.department}</div>
      <div>Sector: <b>${unit.sector || 'Patrol Corridor'}</b></div>
      <div>Unit Commander: <b>${unit.unit_lead}</b></div>
      <div>Status: <b style="color:${statColor};">${unit.status}</b></div>
      <div>Speed: <b>${unit.speed_kmh} km/h</b> | Heading: <b>${unit.heading}°</b></div>
      ${incidentBlock}
      <div style="margin-top:8px; display:flex; gap:6px;">
        <button onclick="window.trackResponderOnMap('${unit.code}')" style="background:#080F1E; color:#00D9FF; border:1px solid #00D9FF; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:10px; font-weight:bold;">
          🎯 Follow Live
        </button>
        <button onclick="window.resetResponderToPatrol('${unit.code}')" style="background:#101B2D; color:#94A3B8; border:1px solid #64748B; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:10px;">
          🔄 Reset Patrol
        </button>
      </div>
    </div>
  `;
}

function updateMapResponders(responders) {
  if (!responders || !Array.isArray(responders)) return;

  const mapList = [
    { name: 'command', map: commandMap },
    { name: 'gis', map: gisMap }
  ];

  mapList.forEach(({ name, map }) => {
    if (!map) return;
    if (!responderMarkers[name]) responderMarkers[name] = {};

    responders.forEach(unit => {
      const marker = responderMarkers[name][unit.code];
      const icon = createResponderIcon(unit);
      const popupHtml = renderResponderPopupContent(unit);

      if (!marker) {
        const m = L.marker([unit.lat, unit.lon], { icon }).addTo(map);
        m.bindPopup(popupHtml);
        responderMarkers[name][unit.code] = m;
      } else {
        marker.setLatLng([unit.lat, unit.lon]);
        marker.setIcon(icon);
        if (marker.getPopup() && marker.isPopupOpen()) {
          marker.setPopupContent(popupHtml);
        }
      }
    });
  });

  // If a unit is actively tracked by operator
  if (activeTrackedUnitCode) {
    const trackedUnit = responders.find(u => u.code === activeTrackedUnitCode);
    if (trackedUnit) {
      const activeMap = gisMap || commandMap;
      if (activeMap) {
        if (trackedUnit.assigned_incident) {
          const inc = trackedUnit.assigned_incident;
          if (responderRouteLayer) {
            activeMap.removeLayer(responderRouteLayer);
          }
          responderRouteLayer = L.polyline([[trackedUnit.lat, trackedUnit.lon], [inc.target_lat, inc.target_lon]], {
            color: trackedUnit.type === 'FIRE' ? '#EF4444' : '#00D9FF',
            weight: 4,
            dashArray: '6, 8',
            opacity: 0.95
          }).addTo(activeMap);
        }
      }
    }
  }
}

function trackResponderOnMap(teamCode) {
  activeTrackedUnitCode = teamCode;
  const activeMap = gisMap || commandMap;
  if (!activeMap) return;

  const m = (responderMarkers.gis && responderMarkers.gis[teamCode]) || (responderMarkers.command && responderMarkers.command[teamCode]);
  if (m) {
    activeMap.flyTo(m.getLatLng(), 15, { duration: 1.0 });
    m.openPopup();
  }

  if (window.showToast) {
    window.showToast(`🎯 Live GPS Tracking Engaged: Unit ${teamCode}`);
  }
}

function resetResponderToPatrol(teamCode) {
  fetch('/api/responders/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `team_code=${encodeURIComponent(teamCode)}`
  }).then(() => {
    if (responderRouteLayer && (gisMap || commandMap)) {
      (gisMap || commandMap).removeLayer(responderRouteLayer);
      responderRouteLayer = null;
    }
    activeTrackedUnitCode = null;
    if (window.showToast) window.showToast(`Unit ${teamCode} returned to standard patrol`);
    if (window.loadMapData) window.loadMapData();
  });
}

// Smooth Region Navigation Jump
function jumpToRegion(regionKey) {
  const reg = REGION_COORDINATES[regionKey];
  if (!reg) return;

  [commandMap, gisMap].forEach(map => {
    if (!map) return;
    if (reg.bounds) {
      map.flyToBounds(reg.bounds, { padding: [20, 20], maxZoom: 8, duration: 1.2 });
    } else {
      map.flyTo(reg.center, reg.zoom, { duration: 1.2 });
    }
  });

  if (window.showToast) {
    window.showToast(`Map View: ${reg.name}`);
  }
}

// Function to plot emergency route polyline
async function plotRoute(fromLat, fromLon, toLat, toLon) {
  try {
    const formData = new FormData();
    formData.append('from_lat', fromLat);
    formData.append('from_lon', fromLon);
    formData.append('to_lat', toLat);
    formData.append('to_lon', toLon);

    const res = await fetch('/api/geo/route', { method: 'POST', body: formData });
    const data = await res.json();

    const activeMap = gisMap || commandMap;
    if (!activeMap) return;

    if (routeLayer) {
      activeMap.removeLayer(routeLayer);
    }

    const latlngs = data.route_waypoints.map(wp => [wp.lat, wp.lon]);
    routeLayer = L.polyline(latlngs, {
      color: '#00D9FF',
      weight: 5,
      dashArray: '8, 8',
      opacity: 0.95
    }).addTo(activeMap);

    activeMap.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });

    if (window.showToast) {
      window.showToast(`Emergency Route Plotted: ${data.road_distance_km} km | Travel Time: ${data.estimated_travel_time_min} mins`);
    }
  } catch (err) {
    console.error("Error plotting route:", err);
  }
}

window.initMaps = initMaps;
window.ensureGisMap = ensureGisMap;
window.loadMapData = loadMapData;
window.updateMapDrone = updateMapDrone;
window.updateMapResponders = updateMapResponders;
window.trackResponderOnMap = trackResponderOnMap;
window.resetResponderToPatrol = resetResponderToPatrol;
window.plotRoute = plotRoute;
window.jumpToRegion = jumpToRegion;
window.REGION_COORDINATES = REGION_COORDINATES;
