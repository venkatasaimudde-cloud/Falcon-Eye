# 🦅 FALCON EYE
### AI-Powered Smart Public Safety & Emergency Intelligence Platform

> **"See the Situation. Understand the Risk. Respond Faster."**  
> *Theme: Track 1 — AI for Smart Public Safety*

---

## 🌐 Live Demo & Deployment Links

| Resource | Link / Status | Description |
| :--- | :--- | :--- |
| **Active Live Command Center** | [🚀 Open Live Demo](https://input-rental-recommends-colin.trycloudflare.com) | Live public HTTPS Command Center (Online now) |
| **Interactive API Docs (Swagger)** | [📖 View Swagger Docs](https://input-rental-recommends-colin.trycloudflare.com/docs) | REST API Explorer & Schema Reference |
| **GitHub Repository** | [📂 Falcon-Eye Repository](https://github.com/venkatasaimudde-cloud/Falcon-Eye) | Official Source Code & Release v1.0 |

---

## 🌟 Executive Summary

**FALCON EYE** is a full-stack, enterprise-grade public safety command-center platform integrating real-time computer vision, drone (UAV) telemetry simulation, geospatial intelligence (GIS), ethical facial privacy protection, explainable multi-factor situational risk scoring, multilingual citizen reporting, and automated digital evidence management into a single centralized system.

Built with a modern **deep navy (#080F1E)** and **electric cyan (#00D9FF)** command-center aesthetic, the application provides dual user interfaces:
1. **Futuristic Web Command Center** (FastAPI + HTML5/CSS3/Vanilla JS + Leaflet.js + Chart.js + WebSockets) delivering real-time HUD telemetry, smooth responsive mapping, interactive video canvas, and a 1-click 9-stage judge demonstration.
2. **Streamlit Command Center Dashboard** (`streamlit run streamlit_app.py`) sharing the exact same relational database, AI models, and incident records.

---

## 🏗️ System Architecture

```
                       ┌────────────────────────────────────────────────────────┐
                       │          FALCON EYE UNIFIED COMMAND CENTER             │
                       │  (Web Command Center / Streamlit Incident Dashboard)   │
                       └───────────────────▲─────────────────▲──────────────────┘
                                           │                 │
                                REST API   │                 │ Real-Time WebSockets
                                           ▼                 ▼
                       ┌────────────────────────────────────────────────────────┐
                       │             FASTAPI ASYNCHRONOUS GATEWAY               │
                       │            (Python 3.10+ / Uvicorn Engine)             │
                       └───────────▲──────────────────────────────▲─────────────┘
                                   │                              │
         ┌─────────────────────────┴─────────┐          ┌─────────┴────────────────────────┐
         │       AI COMPUTER VISION SUITE    │          │     BACKEND INTELLIGENCE ENGINES │
         ├───────────────────────────────────┤          ├──────────────────────────────────┤
         │ • YOLOv8 Object Detection         │          │ • UAV Drone Kinematics Simulator │
         │ • Dynamic Crowd Density & Heatmaps│          │ • Leaflet Geospatial GIS Routing │
         │ • Multi-Spectral Fire & Smoke     │          │ • Multilingual Reporter (TE/HI)  │
         │ • Vehicular Collision & Hazard Det│          │ • ReportLab PDF Incident Dossier │
         │ • MediaPipe Face Privacy Blurring │          │ • Explainable Risk Scoring Engine│
         └─────────────────────────┬─────────┘          └─────────┬────────────────────────┘
                                   │                              │
                                   └──────────────┬───────────────┘
                                                  ▼
                       ┌────────────────────────────────────────────────────────┐
                       │         PERSISTENCE & EVIDENCE REPOSITORY              │
                       │  • SQLite Database (PostgreSQL/PostGIS Compatible)     │
                       │  • Evidence Vault with SHA-256 Cryptographic Hashes    │
                       │  • Tamper-Evident Immutable Audit Log Trails           │
                       └────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Modules & Capabilities

### 1. Real Computer Vision Engine
- **YOLOv8 Nano Object Detection**: Real-time localization and tallying of pedestrians, cars, buses, trucks, motorcycles, and backpacks.
- **Dedicated Multi-Spectral Fire & Smoke Classifier**: Evaluates HSV flame boundaries, dynamic flicker frequency, and edge degradation (smoke diffusion). Does NOT masquerade standard COCO classes as fire.
- **Accident & Hazard Engine**: Analyzes bounding-box overlap (IoU) for vehicle collisions and geometric aspect ratio (`width / height > 1.15`) for fallen/incapacitated pedestrians.
- **Responsible Facial Intelligence & Privacy**: Applies Gaussian face blurring **by default**. Includes an isolated, consent-based authorized personnel badge verification terminal (`FE-SEC-091`, `FE-SEC-042`).

### 2. Intelligent Crowd Monitoring
- Real-time pedestrian counting and dynamic safety classification:
  - 🟢 **GREEN (< 15):** Normal pedestrian flow.
  - 🟡 **YELLOW (15 - 30):** Increasing density advisory.
  - 🟠 **ORANGE (31 - 50):** High congestion; crowd marshaling advisory.
  - 🔴 **RED (> 50):** Critical threshold exceeded; stampede prevention protocol.
- Computes spatial 2D Gaussian density heatmaps overlaid on video feeds.

### 3. Software-Based Drone Telemetry Simulator
- Transparently labeled as **SIMULATED TELEMETRY / DEMO DATA** for academic integrity.
- Real-time kinematic simulation of UAV `FALCON-UAV-ALPHA-1`:
  - GPS latitude/longitude movement across urban waypoints.
  - Realistic altitude AGL (45m – 120m), speed (15 – 45 km/h), and battery discharge.
  - Aerial surveillance camera view with animated crosshairs, pitch ladder, and compass ribbon.
  - Commands: `START PATROL`, `HOVER`, `DISPATCH TO INCIDENT`, and `RETURN TO HOME (RTH)`.

### 4. Geospatial Intelligence (GIS) & Emergency Route Engine
- Interactive Leaflet map on CartoDB Dark Matter tiles.
- Pins CCTV camera nodes, active incident alert pulses, UAV flight paths, and emergency facilities.
- Computes Haversine distance and siren travel times to Osmania General Hospital, Moghalpura Fire Station, and City Police HQ.
- Generates turn-by-turn emergency vehicle route polylines.

### 5. Multilingual Citizen Reporter
- Accepts citizen emergency reports in **Telugu (తెలుగు)**, **Hindi (हिन्दी)**, or **English**.
- Automatically translates local languages into structured English dossiers for the control-room operator, auto-assigning categories and urgency levels.

### 6. Incident Lifecycle, Evidence Vault & PDF Export
- Strict workflow: `DETECTED` &rarr; `PENDING_REVIEW` &rarr; `VERIFIED` &rarr; `ACKNOWLEDGED` &rarr; `ASSIGNED` &rarr; `RESOLVED`.
- Cryptographic SHA-256 evidence hashing for chain-of-custody compliance.
- Generates downloadable official PDF Incident Dossiers using `ReportLab`.
- Exports all incident records to CSV for municipal analytics.

---

## 🏆 9-Stage Hackathon Demonstration ("START PUBLIC SAFETY DEMO")

To ensure an impressive demonstration for hackathon judges with zero dependency on physical hardware or paid external APIs, click the **"START PUBLIC SAFETY DEMO"** button in the sidebar:

| Stage | Name | Description |
|:---:|:---|:---|
| **1** | **Stream Ingestion** | Ingests sample public surveillance feed (CAM-01 Central Plaza). |
| **2** | **YOLOv8 Inference** | Runs real object detection on CPU with latency under 30ms. |
| **3** | **Pedestrian Tally** | Localizes bounding boxes and computes exact people count. |
| **4** | **Crowd Threshold** | Analyzes density and flags high congestion state. |
| **5** | **Incident Generation** | Creates incident record with SHA-256 cryptographic evidence hash. |
| **6** | **GIS Geolocation** | Plots pulsating alert pin on Leaflet GIS map. |
| **7** | **Operator Verification** | Lead Operator reviews evidence and verifies situational risk. |
| **8** | **Tactical Dispatch** | Dispatches nearest Rapid Response Police Unit with route ETA. |
| **9** | **PDF Dossier Export** | Generates sealed official ReportLab PDF report ready for download. |

---

## 👥 7-Day Team Development Checklist

| Member | Focus Area | Completed Deliverables |
|:---|:---|:---|
| **Member 1 (Frontend Lead)** | UI/UX & Command Center | • Cyberpunk Command Center (`index.html`, `style.css`)<br/>• KPI Cards, Glassmorphism panels, Audio alerts<br/>• Streamlit Dashboard (`streamlit_app.py`) |
| **Member 2 (AI/Vision Lead)** | Computer Vision & Models | • YOLOv8 Object Detector (`detector.py`)<br/>• Crowd Heatmap & Density Engine (`crowd_analyzer.py`)<br/>• Multi-Spectral Fire/Smoke Detector (`fire_smoke_detector.py`)<br/>• MediaPipe Face Privacy Blurring (`face_privacy.py`) |
| **Member 3 (Backend Lead)** | API, Database & Reports | • FastAPI REST Gateway & WebSockets (`app.py`)<br/>• SQLAlchemy Models & SQLite DB (`models.py`)<br/>• ReportLab PDF Dossier Generator (`pdf_generator.py`)<br/>• Multilingual Emergency Assistant (`multilingual_engine.py`) |
| **Member 4 (GIS & Integration Lead)** | Geospatial, Drone & QA | • Leaflet Map & Routing (`map.js`, `geo_engine.py`)<br/>• UAV Telemetry Kinematics Simulator (`drone_simulator.py`)<br/>• Automated 9-Stage Judge Orchestrator (`demo.js`)<br/>• Automated Test Suite (14 passing tests) |

---

## ⚙️ Quickstart & Installation

### 1. Requirements
- Python 3.10+ (Tested and verified on Python 3.14)
- Pip & Virtualenv (optional)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Generate Sample Media
```bash
python sample_data/seed_db.py
python sample_data/generate_samples.py
```

### 4. Launch the Platform
```bash
python run.py
```
- **Web Command Center:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. (Optional) Run Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```

### 6. Run Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 🔒 Security & Privacy Guarantees

1. **Privacy by Default**: Civilian faces are automatically blurred prior to operator viewing or database archiving.
2. **Explainable Risk Scoring**: The situational risk score evaluates purely environmental and hazard factors (flame presence, crowd density, time of day). It **never** profiles or predicts behavior for individual humans.
3. **Chain-of-Custody**: All evidence snapshots are hashed using SHA-256 upon ingestion and recorded in an immutable audit log.
4. **No Real Emergency Dispatch**: System is configured for training and decision-support only; never directly triggers live 911/100 calls without authorized human review.

---

## 📈 Future Roadmap

- [ ] **Physical MAVLink Drone Integration**: Connect PX4/ArduPilot telemetry via DroneKit or MAVSDK.
- [ ] **Thermal FLIR Camera Support**: Ingest radiometric thermal video streams for nighttime search and rescue.
- [ ] **PostGIS Spatial Indexing**: Migrate SQLite to PostgreSQL + PostGIS with spatial clustering for city-wide scaling.
- [ ] **Edge Deployment**: Optimize YOLOv8 models with TensorRT / ONNX Runtime for NVIDIA Jetson edge gateways.
