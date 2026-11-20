"""
Unit Tests for FALCON EYE FastAPI Endpoints
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "FALCON EYE" in data["system"]


def test_stats_endpoint():
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_incidents" in data
    assert "active_incidents" in data
    assert "drone_battery" in data


def test_incidents_crud():
    # 1. List
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert isinstance(incidents, list)
    assert len(incidents) > 0

    # 2. Create
    payload = {
        "title": "Test AI Stampede Hazard",
        "category": "CROWD_CONGESTION",
        "severity": "HIGH",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "location_name": "Test Terminal",
        "confidence": 0.89,
        "risk_score": 68.0,
        "description": "Test incident for verification"
    }
    create_res = client.post("/api/incidents", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["incident_number"].startswith("INC-FE")

    # 3. Status update
    patch_res = client.patch(f"/api/incidents/{created['id']}/status", json={"status": "VERIFIED", "notes": "Approved by auditor"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "VERIFIED"


def test_drone_telemetry_endpoint():
    res = client.get("/api/drone/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "altitude_m" in data
    assert "speed_kmh" in data
    assert data["is_simulated"] is True


def test_hackathon_demo_stage():
    res = client.post("/api/demo/step/1")
    assert res.status_code == 200
    data = res.json()
    assert data["stage"] == 1
    assert data["status"] == "COMPLETED"


def test_multilingual_citizen_report():
    payload = {
        "text": "ఒక వ్యక్తి బస్ స్టాండ్ లో కింద పడిపోయాడు, సహాయం కావాలి",
        "language": "te",
        "location_name": "South Depot"
    }
    res = client.post("/api/citizen/report", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "RECEIVED"
    assert data["language"] == "Telugu"
    assert "Translated" in data["translated_english"]
