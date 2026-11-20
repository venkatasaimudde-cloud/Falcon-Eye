import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.services.responder_service import responder_service, haversine_km, bearing_degrees


def test_haversine_and_bearing():
    # Hyderabad to Warangal distance ~130-150 km
    dist = haversine_km(17.3850, 78.4867, 17.9784, 79.5941)
    assert 120.0 < dist < 160.0

    bearing = bearing_degrees(17.3850, 78.4867, 17.3850, 78.5867)
    assert 85.0 < bearing < 95.0


def test_responder_fleet_initialization():
    units = responder_service.get_live_units()
    assert len(units) >= 8

    # Verify presence of police and fire units
    types = {u["type"] for u in units}
    assert "POLICE" in types
    assert "FIRE" in types
    assert "MEDICAL" in types


def test_dispatch_and_cad_message():
    res = responder_service.dispatch_unit_to_incident(
        team_code="RPU-TG-01",
        incident_id=999,
        incident_number="INC-TEST-999",
        title="Test Chemical Hazard",
        category="FIRE_SMOKE",
        severity="CRITICAL",
        target_lat=17.3650,
        target_lon=78.4750,
        location_name="Charminar Central"
    )

    assert res["status"] == "SUCCESS"
    assert res["unit"]["status"] == "DISPATCHED"
    assert "dispatch_message" in res
    assert "Charminar Division Control Room" in res["dispatch_message"]["target_station"]

    # Verify message appended to log
    messages = responder_service.get_messages()
    assert len(messages) > 0
    assert any("INC-TEST-999" in m.get("message", "") for m in messages)


def test_reset_unit():
    responder_service.reset_unit("RPU-TG-01")
    unit = responder_service.units["RPU-TG-01"]
    assert unit["status"] == "PATROLLING"
    assert unit["assigned_incident"] is None
