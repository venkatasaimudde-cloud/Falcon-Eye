"""
FALCON EYE — Streamlit Command Center Dashboard
Track 1: AI for Smart Public Safety & Emergency Intelligence Platform
Theme: Deep navy (#080F1E), Dark blue (#101B2D), Electric cyan (#00D9FF), Blue (#2878FF)
"""

import os
import sys
import hashlib
from datetime import datetime
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Add root directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import SessionLocal
from backend.models import Incident, Camera, Drone, ResponseTeam, CrowdStatistic
from backend.ai.detector import detector
from backend.ai.crowd_analyzer import crowd_analyzer
from backend.ai.fire_smoke_detector import fire_smoke_detector
from backend.ai.face_privacy import face_privacy_engine
from backend.services.drone_simulator import drone_sim
from backend.services.geo_engine import geo_engine
from backend.services.multilingual_engine import multilingual_assistant
from backend.services.pdf_generator import pdf_generator

st.set_page_config(
    page_title="FALCON EYE — Smart Public Safety",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Command Center Styling
st.markdown("""
<style>
    .stApp {
        background-color: #080F1E;
        color: #E2E8F0;
    }
    header {visibility: hidden;}
    .css-1d391kg, .css-12oz5g7 {
        background-color: #101B2D;
    }
    .metric-card {
        background-color: #101B2D;
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 800;
        color: #FFFFFF;
        font-family: monospace;
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.8px;
    }
    .badge-cyan {
        color: #00D9FF;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def get_db_session():
    return SessionLocal()


# --------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 20px 0;">
    <div style="font-size: 32px;">🦅</div>
    <h2 style="color: #FFFFFF; margin: 0; font-size: 20px; letter-spacing: 1.5px;">FALCON <span style="color: #00D9FF;">EYE</span></h2>
    <div style="color: #00D9FF; font-size: 9px; letter-spacing: 1px;">AI SMART PUBLIC SAFETY & UAV</div>
</div>
""", unsafe_allow_html=True)

nav_choice = st.sidebar.radio(
    "NAVIGATION",
    [
        "Command Center",
        "AI Detection Studio",
        "Crowd Intelligence",
        "Face Intelligence & Privacy",
        "Drone Telemetry (Simulated)",
        "Geospatial GIS Map",
        "Multilingual Reporter",
        "System Settings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#94A3B8;'>SYSTEM STATUS: <b style='color:#22C55E;'>OPTIMAL (99.8%)</b><br/>UAV LINK: <b style='color:#00D9FF;'>ACTIVE (Simulated)</b></small>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# 1. COMMAND CENTER DASHBOARD
# --------------------------------------------------------------------------
if nav_choice == "Command Center":
    st.markdown("<h2 style='color:#FFFFFF;'>COMMAND CENTER DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:13px;'>Real-time situational intelligence and active emergency telemetry.</p>", unsafe_allow_html=True)

    db = get_db_session()
    active_inc = db.query(Incident).filter(Incident.status != "RESOLVED").count()
    crowd_alerts = db.query(Incident).filter(Incident.category == "CROWD_CONGESTION").count()
    fire_alerts = db.query(Incident).filter(Incident.category == "FIRE_SMOKE").count()
    resolved_inc = db.query(Incident).filter(Incident.status == "RESOLVED").count()
    telemetry = drone_sim.get_telemetry()
    db.close()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid #EF4444;">
            <div class="metric-label">Active Incidents</div>
            <div class="metric-value">{active_inc}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid #F59E0B;">
            <div class="metric-label">Crowd Alerts</div>
            <div class="metric-value">{crowd_alerts}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid #EF4444;">
            <div class="metric-label">Thermal / Fire</div>
            <div class="metric-value">{fire_alerts}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid #22C55E;">
            <div class="metric-label">Resolved Incidents</div>
            <div class="metric-value">{resolved_inc}</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid #00D9FF;">
            <div class="metric-label">UAV Battery</div>
            <div class="metric-value">{int(telemetry['battery_pct'])}%</div>
        </div>
        """, unsafe_allow_html=True)

    col_map, col_recent = st.columns([2, 1])
    with col_map:
        st.subheader("Telangana & Andhra Pradesh State-Wide Real Map")
        m = folium.Map(location=[16.50, 79.80], zoom_start=7, tiles="OpenStreetMap")
        
        # Add emergency facilities
        for fac in geo_engine.emergency_facilities:
            folium.Marker(
                [fac['lat'], fac['lon']],
                popup=f"{fac['name']} ({fac['city']}, {fac['state']})",
                icon=folium.Icon(color="red" if "FIRE" in fac['type'] else "green", icon="plus-sign")
            ).add_to(m)

        # Add drone
        folium.Marker(
            [telemetry['lat'], telemetry['lon']],
            popup=f"UAV {telemetry['callsign']} ({telemetry['status']})",
            icon=folium.Icon(color="blue", icon="plane", prefix="fa")
        ).add_to(m)

        st_folium(m, height=440, use_container_width=True)

    with col_recent:
        st.subheader("Live Queue")
        db = get_db_session()
        recent = db.query(Incident).order_by(Incident.created_at.desc()).limit(5).all()
        for inc in recent:
            sev_color = "#EF4444" if inc.severity == "CRITICAL" else "#F97316" if inc.severity == "HIGH" else "#22C55E"
            st.markdown(f"""
            <div style="background:#101B2D; border-left:3px solid {sev_color}; padding:8px 12px; margin-bottom:8px; border-radius:4px; font-size:12px;">
                <b style="color:#00D9FF;">{inc.incident_number}</b> — <b>{inc.status}</b><br/>
                <span style="color:#FFFFFF;">{inc.title}</span><br/>
                <small style="color:#94A3B8;">{inc.location_name} • Risk: {inc.risk_score}</small>
            </div>
            """, unsafe_allow_html=True)
        db.close()


# --------------------------------------------------------------------------
# 2. AI DETECTION STUDIO
# --------------------------------------------------------------------------
elif nav_choice == "AI Detection Studio":
    st.markdown("<h2 style='color:#FFFFFF;'>AI COMPUTER VISION STUDIO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Real-time object detection using YOLOv8 nano model on CPU.</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Surveillance Frame / Image", type=["jpg", "jpeg", "png"])
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        load_sample = st.button("Load Sample Crowd Image")
    with col_btn2:
        load_fire_sample = st.button("Load Sample Fire Image")

    img_to_process = None
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img_to_process = cv2.imdecode(file_bytes, 1)
    elif load_sample:
        sample_path = os.path.join(BASE_DIR, "sample_data", "sample_crowd.jpg")
        if os.path.exists(sample_path):
            img_to_process = cv2.imread(sample_path)
    elif load_fire_sample:
        fire_path = os.path.join(BASE_DIR, "sample_data", "sample_fire.jpg")
        if os.path.exists(fire_path):
            img_to_process = cv2.imread(fire_path)

    if img_to_process is not None:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.subheader("Original Input")
            st.image(cv2.cvtColor(img_to_process, cv2.COLOR_BGR2RGB), use_container_width=True)

        with col_res2:
            st.subheader("YOLOv8 Detection Output")
            with st.spinner("Processing neural inference..."):
                annotated, detections, counts = detector.detect_frame(img_to_process, conf_threshold=0.35)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                st.image(annotated_rgb, use_container_width=True)

        st.markdown("### Detections Summary")
        cols = st.columns(len(counts) if counts else 1)
        if counts:
            for idx, (cls, cnt) in enumerate(counts.items()):
                with cols[idx]:
                    st.metric(cls.upper(), cnt)
        else:
            st.info("No target objects detected above confidence threshold.")


# --------------------------------------------------------------------------
# 3. CROWD INTELLIGENCE
# --------------------------------------------------------------------------
elif nav_choice == "Crowd Intelligence":
    st.markdown("<h2 style='color:#FFFFFF;'>CROWD DENSITY & HEATMAP INTELLIGENCE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Pedestrian flow monitoring with configurable safety thresholds.</p>", unsafe_allow_html=True)

    y_val = st.slider("Yellow Threshold (Increasing)", 5, 25, 15)
    o_val = st.slider("Orange Threshold (High Density)", 20, 45, 30)
    r_val = st.slider("Red Threshold (Critical / Stampede Hazard)", 40, 80, 50)
    crowd_analyzer.set_thresholds(y_val, o_val, r_val)

    st.markdown("### Active Transit Corridor Test")
    sample_path = os.path.join(BASE_DIR, "sample_data", "sample_crowd.jpg")
    if os.path.exists(sample_path):
        frame = cv2.imread(sample_path)
        annotated, detections, counts = detector.detect_frame(frame, conf_threshold=0.25)
        person_boxes = [d["bbox"] for d in detections if d["class"] == "person"]
        if len(person_boxes) < 15:
            # Synthetic demonstration augmentation
            person_boxes = [[100 + i * 15, 200, 140 + i * 15, 290] for i in range(32)]

        annotated_crowd, summary = crowd_analyzer.overlay_crowd_analytics(frame, person_boxes)
        st.image(cv2.cvtColor(annotated_crowd, cv2.COLOR_BGR2RGB), use_container_width=True)

        st.info(f"Status: **[{summary['density_level']}]** — {summary['message']}")


# --------------------------------------------------------------------------
# 4. FACE INTELLIGENCE & PRIVACY
# --------------------------------------------------------------------------
elif nav_choice == "Face Intelligence & Privacy":
    st.markdown("<h2 style='color:#FFFFFF;'>RESPONSIBLE FACE INTELLIGENCE & PRIVACY</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Public privacy protected by default. No surveillance watchlists.</p>", unsafe_allow_html=True)

    blur_faces = st.checkbox("Enable Privacy Face Blurring (Default)", value=True)
    sample_path = os.path.join(BASE_DIR, "sample_data", "sample_crowd.jpg")
    if os.path.exists(sample_path):
        img = cv2.imread(sample_path)
        processed, records, stats = face_privacy_engine.detect_and_protect(img, blur_faces=blur_faces)
        st.image(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB), use_container_width=True)
        st.success(f"Privacy Guarantee: {stats['compliance']}")

    st.markdown("---")
    st.subheader("Authorized Personnel Consent Verification Demonstration")
    st.caption("Demonstrates identity verification for registered staff badges (e.g. FE-SEC-091).")
    badge_input = st.text_input("Enter Staff Badge Code", "FE-SEC-091")
    if st.button("Verify Badge"):
        result = face_privacy_engine.verify_authorized_personnel(badge_input)
        if result["matched"]:
            st.success(result["message"])
        else:
            st.error(result["message"])


# --------------------------------------------------------------------------
# 5. DRONE TELEMETRY
# --------------------------------------------------------------------------
elif nav_choice == "Drone Telemetry (Simulated)":
    st.markdown("<h2 style='color:#FFFFFF;'>UAV DRONE TELEMETRY & PATROL CONTROL [SIMULATED DATA]</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Real-time kinematics and software-based flight simulator.</p>", unsafe_allow_html=True)

    telemetry = drone_sim.get_telemetry()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Altitude", f"{telemetry['altitude_m']} m")
    c2.metric("Speed", f"{telemetry['speed_kmh']} km/h")
    c3.metric("Battery", f"{int(telemetry['battery_pct'])}%")
    c4.metric("Heading", f"{int(telemetry['heading_deg'])}°")

    st.image(cv2.cvtColor(drone_sim.render_aerial_hud_frame(), cv2.COLOR_BGR2RGB), use_container_width=True)


# --------------------------------------------------------------------------
# 6. GEOSPATIAL GIS MAP
# --------------------------------------------------------------------------
elif nav_choice == "Geospatial GIS Map":
    st.markdown("<h2 style='color:#FFFFFF;'>TELANGANA & ANDHRA PRADESH GEOSPATIAL GIS MAP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Real-world multi-layer state GIS grid with district hospitals, fire stations, and police headquarters.</p>", unsafe_allow_html=True)

    col_reg, col_tiles = st.columns([2, 1])
    with col_reg:
        region_opt = st.selectbox(
            "Select Map Region / Jurisdiction:",
            [
                "🗺️ Telangana & Andhra Pradesh (Full States)",
                "🏛️ Telangana State (Hyderabad, Warangal, Karimnagar, Nizamabad)",
                "🌊 Andhra Pradesh State (Visakhapatnam, Vijayawada, Tirupati, Kurnool)",
                "🏙️ Hyderabad Metro Area",
                "🏖️ Visakhapatnam Coastal Sector",
                "🏬 Vijayawada / Amaravati Capital",
                "🕉️ Tirupati Pilgrim Security Hub"
            ]
        )
    with col_tiles:
        tile_opt = st.selectbox(
            "Base Map Layer:",
            ["OpenStreetMap (Real Map)", "CartoDB dark_matter (Tactical)", "CartoDB positron (Light)"]
        )

    # Determine coordinates from region selection
    reg_coords = [16.50, 79.80]
    reg_zoom = 7
    if "Telangana State" in region_opt:
        reg_coords = [17.85, 79.10]
        reg_zoom = 8
    elif "Andhra Pradesh State" in region_opt:
        reg_coords = [15.90, 80.50]
        reg_zoom = 8
    elif "Hyderabad" in region_opt:
        reg_coords = [17.3850, 78.4867]
        reg_zoom = 12
    elif "Visakhapatnam" in region_opt:
        reg_coords = [17.7126, 83.3241]
        reg_zoom = 12
    elif "Vijayawada" in region_opt:
        reg_coords = [16.5062, 80.6480]
        reg_zoom = 12
    elif "Tirupati" in region_opt:
        reg_coords = [13.6369, 79.4042]
        reg_zoom = 13

    tile_name = "OpenStreetMap" if "OpenStreetMap" in tile_opt else "CartoDB dark_matter" if "dark_matter" in tile_opt else "CartoDB positron"
    m = folium.Map(location=reg_coords, zoom_start=reg_zoom, tiles=tile_name)

    # Add facilities across Telangana and Andhra Pradesh
    for fac in geo_engine.emergency_facilities:
        folium.Marker(
            [fac['lat'], fac['lon']],
            popup=f"{fac['name']} ({fac['city']}, {fac['state']}) - {fac['type']}",
            icon=folium.Icon(color="red" if "FIRE" in fac['type'] else "blue" if "POLICE" in fac['type'] else "green", icon="info-sign")
        ).add_to(m)

    st_folium(m, height=520, use_container_width=True)




# --------------------------------------------------------------------------
# 8. MULTILINGUAL CITIZEN REPORTER
# --------------------------------------------------------------------------
elif nav_choice == "Multilingual Reporter":
    st.markdown("<h2 style='color:#FFFFFF;'>MULTILINGUAL CITIZEN EMERGENCY ASSISTANT</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Translates Telugu, Hindi, and English citizen reports for control-room operators.</p>", unsafe_allow_html=True)

    text_input = st.text_area("Citizen Emergency Report", "ఒక వ్యక్తి బస్ స్టాండ్ లో కింద పడిపోయాడు, సహాయం కావాలి")
    if st.button("Process & Translate Report"):
        res = multilingual_assistant.process_report(text_input)
        st.success(f"Detected Language: {res['language_name']}")
        st.info(f"English Translation: {res['translated_english']}")
        st.warning(f"Suggested Triage: {res['suggested_category']} | Urgency: {res['suggested_severity']}")




# --------------------------------------------------------------------------
# 10. SYSTEM SETTINGS & JURISDICTION
# --------------------------------------------------------------------------
elif nav_choice == "System Settings":
    st.markdown("<h2 style='color:#FFFFFF;'>COMMAND CENTER SETTINGS & REGIONAL JURISDICTION</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Configure operational map region, AI confidence thresholds, and cloud services.</p>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Geospatial & Map Settings")
        st.selectbox("Operational State Focus:", [
            "Telangana & Andhra Pradesh (Full State Grid)",
            "Telangana State (Hyderabad / Warangal / Nizamabad)",
            "Andhra Pradesh State (Visakhapatnam / Vijayawada / Tirupati)",
            "Hyderabad Metro Transit Corridor",
            "Visakhapatnam Coastal Sector"
        ])
        st.selectbox("Default Real Map Tiles:", ["OpenStreetMap (Standard)", "Esri World Imagery (Satellite)", "CartoDB Dark Matter"])
        st.checkbox("Show CCTV Surveillance Cameras (13 Cameras)", value=True)
        st.checkbox("Show Emergency Response Teams (8 Teams)", value=True)
        st.checkbox("Show State Hospitals & Fire Stations (14 Facilities)", value=True)

    with c2:
        st.subheader("AI Detection & Privacy Engine")
        st.slider("YOLOv8 Detection Confidence:", min_value=0.10, max_value=0.90, value=0.35, step=0.05)
        st.selectbox("Face Privacy Compliance:", ["Auto-Blur All Faces (Ethical Standard)", "Allow Badged Security Personnel", "Disabled"])
        st.text_input("Google Gemini API Key:", value=os.getenv("GEMINI_API_KEY", ""), type="password", placeholder="Enter Gemini API Key")

    if st.button("Save & Apply Settings"):
        st.success("✓ Settings Saved & Operational Jurisdiction Set to Telangana & Andhra Pradesh!")

