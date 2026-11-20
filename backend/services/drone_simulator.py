"""
FALCON EYE - Software-Based Drone Telemetry Simulator
Simulates realistic UAV flight physics, GPS kinematics, battery discharge,
altitude control, and aerial HUD rendering.
Explicitly labeled as DEMO / SIMULATION DATA for hackathon credibility.
Designed with standard MAVLink-ready data structures for future physical UAV integration.
"""

import time
import math
import random
import threading
from typing import Dict, Any, List
from datetime import datetime
import numpy as np
import cv2


class DroneSimulator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DroneSimulator, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return

        self.callsign = "FALCON-UAV-ALPHA-1"
        self.model = "Falcon SkyScout-X4 Quad-Rotor"
        self.is_running = True
        self.is_simulated = True  # Transparent labeling

        # Base operational center (e.g., Smart City Command Center / Central Plaza)
        self.home_lat = 17.3850
        self.home_lon = 78.4867

        # Current telemetry state
        self.lat = 17.3850
        self.lon = 78.4867
        self.altitude = 65.0      # meters AGL
        self.speed = 28.5         # km/h
        self.battery = 94.0       # percentage
        self.heading = 145.0      # compass degrees
        self.status = "PATROLLING"  # IDLE, PATROLLING, RESPONDING, RETURNING
        self.target_zone = "Central Transit Corridor"

        # Waypoints for perimeter patrol
        self.waypoints = [
            (17.3850, 78.4867, "Central Station"),
            (17.3895, 78.4890, "North Gate Plaza"),
            (17.3870, 78.4940, "East Commercial Hub"),
            (17.3815, 78.4910, "South Metro Terminal"),
            (17.3820, 78.4830, "West Civic Center")
        ]
        self.current_wp_idx = 0
        self.history: List[Dict[str, Any]] = []
        self.max_history = 50

        # Background simulation thread
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.thread.start()
        self.initialized = True

    def _simulation_loop(self):
        """Continuously update drone telemetry."""
        while True:
            if self.is_running:
                with self.lock:
                    self._update_kinematics()
            time.sleep(1.0)

    def _update_kinematics(self):
        """Update coordinates towards current waypoint."""
        if self.status == "IDLE":
            self.speed = 0.0
            return

        target_lat, target_lon, target_name = self.waypoints[self.current_wp_idx]

        # Calculate vector to target
        d_lat = target_lat - self.lat
        d_lon = target_lon - self.lon
        dist = math.sqrt(d_lat**2 + d_lon**2)

        # Reached waypoint threshold
        if dist < 0.0003:
            self.current_wp_idx = (self.current_wp_idx + 1) % len(self.waypoints)
            self.target_zone = self.waypoints[self.current_wp_idx][2]
            return

        # Heading calculation
        rad = math.atan2(d_lon, d_lat)
        self.heading = round((math.degrees(rad) + 360) % 360, 1)

        # Move forward based on speed
        step = 0.00015 * (self.speed / 30.0)
        self.lat += (d_lat / dist) * step
        self.lon += (d_lon / dist) * step

        # Add slight natural atmospheric drift
        self.lat += random.uniform(-0.00001, 0.00001)
        self.lon += random.uniform(-0.00001, 0.00001)

        # Altitude small fluctuation
        self.altitude = round(65.0 + math.sin(time.time() / 5.0) * 4.0, 1)

        # Speed variation
        self.speed = round(28.0 + math.sin(time.time() / 3.0) * 3.5, 1)

        # Battery discharge (gradual simulated drain)
        self.battery = max(5.0, round(self.battery - 0.015, 2))

        # Record telemetry history
        point = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6),
            "altitude": self.altitude,
            "speed": self.speed,
            "battery": self.battery,
            "heading": self.heading,
            "status": self.status,
            "zone": self.target_zone,
            "is_simulation": True
        }
        self.history.append(point)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns the current real-time telemetry snapshot."""
        with self.lock:
            return {
                "callsign": self.callsign,
                "model": self.model,
                "lat": round(self.lat, 6),
                "lon": round(self.lon, 6),
                "altitude_m": self.altitude,
                "speed_kmh": self.speed,
                "battery_pct": self.battery,
                "heading_deg": self.heading,
                "status": self.status,
                "target_zone": self.target_zone,
                "is_simulated": True,
                "simulation_label": "SIMULATED TELEMETRY (DEMO DATA)",
                "signal_strength": "100% LINK (915 MHz Telemetry)",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    def get_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.history)

    def start_sim(self):
        with self.lock:
            self.is_running = True
            if self.status == "IDLE":
                self.status = "PATROLLING"

    def stop_sim(self):
        with self.lock:
            self.is_running = False
            self.status = "IDLE"

    def dispatch_to_incident(self, lat: float, lon: float, zone_name: str = "Active Incident"):
        """Task drone to rush to an incident location."""
        with self.lock:
            self.status = "RESPONDING"
            self.target_zone = zone_name
            self.speed = 42.0  # High-speed response sprint
            # Temporarily set waypoint
            self.waypoints.insert(self.current_wp_idx, (lat, lon, zone_name))

    def return_to_home(self):
        """Order Return to Launch / Home base."""
        with self.lock:
            self.status = "RETURNING"
            self.target_zone = "Command Station Helipad"
            self.waypoints.insert(self.current_wp_idx, (self.home_lat, self.home_lon, "Base Helipad"))

    def render_aerial_hud_frame(self) -> np.ndarray:
        """
        Generates a synthetic aerial surveillance video frame with
        futuristic drone HUD, crosshairs, pitch ladder, and telemetry overlay.
        """
        # Create dark background simulating urban aerial camera
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Gradient background
        for y in range(480):
            val = int(25 + (y / 480) * 35)
            frame[y, :] = (val - 10, val, val + 15)

        # Draw simulated urban road grid lines
        cv2.line(frame, (100, 480), (280, 200), (45, 60, 75), 2)
        cv2.line(frame, (540, 480), (360, 200), (45, 60, 75), 2)
        cv2.line(frame, (0, 350), (640, 350), (40, 55, 70), 1)
        cv2.line(frame, (0, 280), (640, 280), (40, 55, 70), 1)

        # Draw Drone Crosshair in center
        cx, cy = 320, 240
        cv2.circle(frame, (cx, cy), 45, (0, 217, 255), 1)
        cv2.line(frame, (cx - 60, cy), (cx - 15, cy), (0, 217, 255), 1)
        cv2.line(frame, (cx + 15, cy), (cx + 60, cy), (0, 217, 255), 1)
        cv2.line(frame, (cx, cy - 60), (cx, cy - 15), (0, 217, 255), 1)
        cv2.line(frame, (cx, cy + 15), (cx, cy + 60), (0, 217, 255), 1)

        # Drone Pitch Indicator
        cv2.line(frame, (cx - 30, cy - 25), (cx + 30, cy - 25), (0, 217, 255), 1)
        cv2.line(frame, (cx - 30, cy + 25), (cx + 30, cy + 25), (0, 217, 255), 1)

        # Telemetry HUD Text
        with self.lock:
            alt = self.altitude
            spd = self.speed
            bat = self.battery
            hdg = self.heading
            stat = self.status
            zone = self.target_zone

        # HUD Top Banner
        cv2.rectangle(frame, (0, 0), (640, 35), (8, 15, 30), -1)
        cv2.line(frame, (0, 35), (640, 35), (0, 217, 255), 1)
        cv2.putText(frame, f"FALCON-UAV-1 [DEMO SIMULATION] | STATUS: {stat} | ZONE: {zone}",
                    (15, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 217, 255), 1, cv2.LINE_AA)

        # HUD Left Ladder (Altitude)
        cv2.rectangle(frame, (10, 180), (80, 300), (8, 15, 30), -1)
        cv2.rectangle(frame, (10, 180), (80, 300), (0, 217, 255), 1)
        cv2.putText(frame, "ALT AGL", (15, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 200, 240), 1)
        cv2.putText(frame, f"{alt}m", (15, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # HUD Right Ladder (Speed & Battery)
        cv2.rectangle(frame, (560, 180), (630, 300), (8, 15, 30), -1)
        cv2.rectangle(frame, (560, 180), (630, 300), (0, 217, 255), 1)
        cv2.putText(frame, "SPEED", (565, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 200, 240), 1)
        cv2.putText(frame, f"{spd}", (565, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(frame, "km/h", (565, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 200, 240), 1)
        cv2.putText(frame, f"BAT {int(bat)}%", (565, 285), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                    (94, 197, 34) if bat > 25 else (68, 68, 239), 1)

        # Compass ribbon bottom
        cv2.rectangle(frame, (220, 440), (420, 470), (8, 15, 30), -1)
        cv2.rectangle(frame, (220, 440), (420, 470), (0, 217, 255), 1)
        cv2.putText(frame, f"HDG: {int(hdg)} DEG [N/E]", (245, 462),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 217, 255), 1, cv2.LINE_AA)

        return frame


# Global singleton instance
drone_sim = DroneSimulator()
