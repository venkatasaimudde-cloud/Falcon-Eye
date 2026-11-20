"""
Unit Tests for UAV Drone Telemetry Simulator
"""

import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.services.drone_simulator import drone_sim


def test_drone_telemetry():
    t = drone_sim.get_telemetry()
    assert t["callsign"] == "FALCON-UAV-ALPHA-1"
    assert t["is_simulated"] is True
    assert 40.0 <= t["altitude_m"] <= 150.0
    assert 0.0 <= t["battery_pct"] <= 100.0


def test_drone_controls():
    # Stop simulation
    drone_sim.stop_sim()
    t = drone_sim.get_telemetry()
    assert t["status"] == "IDLE"

    # Start simulation
    drone_sim.start_sim()
    t = drone_sim.get_telemetry()
    assert t["status"] == "PATROLLING"

    # Dispatch command
    drone_sim.dispatch_to_incident(17.3895, 78.4890, "Metro Incident Zone")
    t = drone_sim.get_telemetry()
    assert t["status"] == "RESPONDING"
    assert t["target_zone"] == "Metro Incident Zone"


def test_drone_aerial_hud():
    frame = drone_sim.render_aerial_hud_frame()
    assert frame is not None
    assert frame.shape == (480, 640, 3)
