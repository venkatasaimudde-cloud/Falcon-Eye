/**
 * FALCON EYE — 9-Stage Hackathon Judge Demonstration Controller
 * Orchestrates the full end-to-end public safety workflow.
 */

let currentDemoStage = 1;
let autoPlayTimer = null;

function openDemoModal() {
  const modal = document.getElementById('demo-modal');
  if (modal) {
    modal.classList.add('active');
    runDemoStage(1);
  }
}

function closeDemoModal() {
  const modal = document.getElementById('demo-modal');
  if (modal) {
    modal.classList.remove('active');
    stopAutoPlay();
  }
}

async function runDemoStage(stageNum) {
  currentDemoStage = stageNum;
  updateStepperUI(stageNum);

  const statusText = document.getElementById('demo-stage-title');
  const descText = document.getElementById('demo-stage-desc');
  const metricsBox = document.getElementById('demo-stage-metrics');
  const screenPreview = document.getElementById('demo-screen-preview');

  if (statusText) statusText.innerText = `Executing Stage ${stageNum}...`;

  try {
    const res = await fetch(`/api/demo/step/${stageNum}`, { method: 'POST' });
    const data = await res.json();

    if (statusText) statusText.innerText = data.title;
    if (descText) descText.innerText = data.description;

    // Render metrics key-values
    if (metricsBox && data.metrics) {
      let html = '<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 12px;">';
      for (const [k, v] of Object.entries(data.metrics)) {
        html += `
          <div style="background: rgba(16, 27, 45, 0.7); border: 1px solid rgba(0, 217, 255, 0.2); border-radius: 6px; padding: 8px 12px;">
            <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">${k.replace(/_/g, ' ')}</div>
            <div style="font-size: 13px; font-weight: 700; color: #00D9FF; margin-top: 2px;">${v}</div>
          </div>
        `;
      }
      html += '</div>';
      metricsBox.innerHTML = html;
    }

    // Visual image/screen update
    if (screenPreview) {
      if (stageNum === 1 || stageNum === 2 || stageNum === 3 || stageNum === 4 || stageNum === 5) {
        screenPreview.innerHTML = `
          <div style="position: relative; width: 100%; height: 260px; background: #000; border-radius: 6px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
            <img src="/sample_data/sample_crowd.jpg" style="max-width: 100%; max-height: 100%; object-fit: contain;" />
            <div style="position: absolute; top: 10px; left: 10px; background: rgba(8,15,30,0.85); border: 1px solid #00D9FF; padding: 4px 10px; border-radius: 4px; font-size: 11px; color: #00D9FF; font-weight: bold;">
              CAM-01 [LIVE STAGE ${stageNum}]
            </div>
            <div style="position: absolute; bottom: 10px; right: 10px; background: rgba(8,15,30,0.85); border: 1px solid #22C55E; padding: 4px 10px; border-radius: 4px; font-size: 11px; color: #22C55E; font-weight: bold;">
              INFERENCE: COMPLETE (28ms)
            </div>
          </div>
        `;
      } else if (stageNum === 6) {
        screenPreview.innerHTML = `
          <div style="width: 100%; height: 260px; background: #080F1E; border: 1px solid #00D9FF; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;">
            <div style="font-size: 40px;">🗺️</div>
            <div style="font-size: 14px; font-weight: 700; color: #FFFFFF;">GIS Geospatial Projection Active</div>
            <div style="font-size: 12px; color: #94A3B8;">Plotted on Leaflet Layer: Central Transit Plaza (17.3850° N, 78.4867° E)</div>
          </div>
        `;
      } else if (stageNum === 7) {
        screenPreview.innerHTML = `
          <div style="width: 100%; height: 260px; background: #101B2D; border: 1px solid #22C55E; border-radius: 6px; padding: 18px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <h4 style="color:#22C55E; font-size:14px;">Operator Verification Checkpoint</h4>
              <span style="background:rgba(34,197,94,0.15); border:1px solid #22C55E; color:#22C55E; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">VERIFIED</span>
            </div>
            <p style="color:#E2E8F0; font-size:12px; margin-top:10px;">Operator: <b>Vikram Sharma (FE-SEC-091)</b></p>
            <p style="color:#E2E8F0; font-size:12px; margin-top:4px;">Verification Decision: <b>Visual match confirmed. Stampede safety protocol enacted.</b></p>
            <p style="color:#00D9FF; font-size:12px; margin-top:4px;">Calculated Risk Index: <b>72.0 / 100 (HIGH RISK)</b></p>
          </div>
        `;
      } else if (stageNum === 8) {
        screenPreview.innerHTML = `
          <div style="width: 100%; height: 260px; background: #101B2D; border: 1px solid #2878FF; border-radius: 6px; padding: 18px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <h4 style="color:#2878FF; font-size:14px;">Tactical Dispatch Command</h4>
              <span style="background:rgba(40,120,255,0.15); border:1px solid #2878FF; color:#2878FF; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">DISPATCHED</span>
            </div>
            <p style="color:#E2E8F0; font-size:12px; margin-top:10px;">Unit: <b>Rapid Police Patrol Unit 04</b></p>
            <p style="color:#E2E8F0; font-size:12px; margin-top:4px;">Optimal Route: <b>1.8 km via Arterial Ring Road</b></p>
            <p style="color:#00D9FF; font-size:12px; margin-top:4px;">Estimated Arrival Time: <b>3.2 Minutes</b></p>
          </div>
        `;
      } else if (stageNum === 9) {
        const downloadUrl = data.metrics ? data.metrics.download_url : '#';
        screenPreview.innerHTML = `
          <div style="width: 100%; height: 260px; background: #080F1E; border: 1px solid #00D9FF; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px;">
            <div style="font-size: 42px;">📄</div>
            <div style="font-size: 15px; font-weight: 800; color: #FFFFFF;">Official PDF Incident Dossier Sealed</div>
            <div style="font-size: 12px; color: #94A3B8;">ReportLab Engine Generated • SHA-256 Integrity Signed</div>
            <a href="${downloadUrl}" target="_blank" class="btn-falcon btn-falcon-primary" style="text-decoration:none;">
              Download Official PDF Dossier
            </a>
          </div>
        `;
      }
    }

    // Refresh application state if in main dashboard
    if (window.loadMapData) window.loadMapData();
    if (window.fetchDashboardStats) window.fetchDashboardStats();

  } catch (err) {
    console.error(`Error executing demo stage ${stageNum}:`, err);
  }
}

function updateStepperUI(activeStage) {
  for (let i = 1; i <= 9; i++) {
    const node = document.getElementById(`step-node-${i}`);
    if (!node) continue;
    node.classList.remove('active', 'completed');
    if (i < activeStage) {
      node.classList.add('completed');
    } else if (i === activeStage) {
      node.classList.add('active');
    }
  }
}

function nextDemoStage() {
  if (currentDemoStage < 9) {
    runDemoStage(currentDemoStage + 1);
  }
}

function prevDemoStage() {
  if (currentDemoStage > 1) {
    runDemoStage(currentDemoStage - 1);
  }
}

function toggleAutoPlay() {
  const btn = document.getElementById('demo-autoplay-btn');
  if (autoPlayTimer) {
    stopAutoPlay();
    if (btn) btn.innerText = "▶ Auto Play";
  } else {
    if (btn) btn.innerText = "⏸ Pause Auto";
    autoPlayTimer = setInterval(() => {
      if (currentDemoStage < 9) {
        runDemoStage(currentDemoStage + 1);
      } else {
        stopAutoPlay();
        if (btn) btn.innerText = "▶ Auto Play";
      }
    }, 3500);
  }
}

function stopAutoPlay() {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }
}

window.openDemoModal = openDemoModal;
window.closeDemoModal = closeDemoModal;
window.runDemoStage = runDemoStage;
window.nextDemoStage = nextDemoStage;
window.prevDemoStage = prevDemoStage;
window.toggleAutoPlay = toggleAutoPlay;
