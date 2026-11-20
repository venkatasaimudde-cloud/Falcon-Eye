"""
FALCON EYE - Dynamic Police & Fire Responder Simulation & Departmental Messaging Service
Features:
- Live patrolling kinematics for Police cruisers, Fire & Rescue tenders, and Ambulances across Telangana & Andhra Pradesh.
- Real-time en-route navigation to incidents with decreasing distance (km) and live ETA countdown.
- Verified arrival detection (switches to ON_SCENE within 50m of target).
- Automated Computer-Aided Dispatch (CAD) & TETRA radio messaging to respective Police Commissionerates and Fire Stations.
"""

import math
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0)**2
    return round(R * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))), 2)


def bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    deg = math.degrees(math.atan2(y, x))
    return round((deg + 360.0) % 360.0, 1)


class ResponderService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResponderService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return

        self.initialized = True
        self.is_running = True
        self.messages: List[Dict[str, Any]] = []

        # Fleet of active response units across Telangana and Andhra Pradesh
        self.units: Dict[str, Dict[str, Any]] = {
            "RPU-TG-01": {
                "code": "RPU-TG-01",
                "name": "Rapid Police Patrol Unit 01 (Hyderabad Metro)",
                "type": "POLICE",
                "department": "Hyderabad City Police Commissionerate",
                "department_station": "Charminar Division Control Room",
                "contact": "100 / +91 40 2785 2400",
                "unit_lead": "Inspector K. Naidu",
                "sector": "Hyderabad Central & Old City",
                "base_lat": 17.3620,
                "base_lon": 78.4740,
                "lat": 17.3620,
                "lon": 78.4740,
                "heading": 85.0,
                "speed_kmh": 32.0,
                "status": "PATROLLING",  # PATROLLING, DISPATCHED, ON_SCENE
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.3616, 78.4747),  # Charminar
                    (17.3710, 78.4800),  # Moazzam Jahi
                    (17.3780, 78.4730),  # Abids
                    (17.3680, 78.4680)   # High Court
                ],
                "patrol_idx": 0
            },
            "FIRE-TG-01": {
                "code": "FIRE-TG-01",
                "name": "Central Fire & Rescue Tender (Hyderabad)",
                "type": "FIRE",
                "department": "Telangana State Disaster Response & Fire Services",
                "department_station": "Moghalpura Fire Station (HQ)",
                "contact": "101 / +91 40 2344 2944",
                "unit_lead": "Station Fire Officer R. Singh",
                "sector": "Hyderabad Urban Fire Zone",
                "base_lat": 17.3630,
                "base_lon": 78.4760,
                "lat": 17.3630,
                "lon": 78.4760,
                "heading": 120.0,
                "speed_kmh": 0.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.3630, 78.4760),
                    (17.3690, 78.4820),
                    (17.3650, 78.4710)
                ],
                "patrol_idx": 0
            },
            "RPU-TG-CYB": {
                "code": "RPU-TG-CYB",
                "name": "Cyberabad Highway Patrol Interceptor",
                "type": "POLICE",
                "department": "Cyberabad Police Commissionerate",
                "department_station": "Madhapur Traffic & Patrol Division",
                "contact": "100 / +91 40 2300 2400",
                "unit_lead": "Sub-Inspector P. Varma",
                "sector": "HITEC City / Financial District",
                "base_lat": 17.4435,
                "base_lon": 78.3772,
                "lat": 17.4435,
                "lon": 78.3772,
                "heading": 210.0,
                "speed_kmh": 36.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.4435, 78.3772),  # HITEC City
                    (17.4334, 78.3866),  # Inorbit Mall
                    (17.4260, 78.3700),  # Biodiversity Junction
                    (17.4380, 78.3600)   # Mindspace Corridor
                ],
                "patrol_idx": 0
            },
            "MED-TG-01": {
                "code": "MED-TG-01",
                "name": "Osmania Advanced Life Support 108 Ambulance",
                "type": "MEDICAL",
                "department": "EMRI 108 Emergency Medical Services Telangana",
                "department_station": "Osmania General Hospital Emergency Bay",
                "contact": "108 / +91 40 2460 0146",
                "unit_lead": "Paramedic Lead Dr. S. Kulkarni",
                "sector": "Hyderabad Central Medical Response",
                "base_lat": 17.3790,
                "base_lon": 78.4760,
                "lat": 17.3790,
                "lon": 78.4760,
                "heading": 30.0,
                "speed_kmh": 25.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.3790, 78.4760),
                    (17.3850, 78.4867),
                    (17.3720, 78.4810)
                ],
                "patrol_idx": 0
            },
            "RPU-TG-WGL": {
                "code": "RPU-TG-WGL",
                "name": "Warangal Quick Reaction Police Patrol",
                "type": "POLICE",
                "department": "Warangal City Police Commissionerate",
                "department_station": "Subedari Police Station, Warangal",
                "contact": "100 / +91 870 244 4250",
                "unit_lead": "Sub-Inspector M. Goud",
                "sector": "Warangal Urban Hub",
                "base_lat": 17.9784,
                "base_lon": 79.5941,
                "lat": 17.9784,
                "lon": 79.5941,
                "heading": 180.0,
                "speed_kmh": 30.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.9784, 79.5941),
                    (17.9850, 79.6020),
                    (17.9650, 79.5890)
                ],
                "patrol_idx": 0
            },
            "FIRE-TG-WGL": {
                "code": "FIRE-TG-WGL",
                "name": "Warangal City Fire & Heavy Foam Tender",
                "type": "FIRE",
                "department": "Telangana State Fire Services - Warangal",
                "department_station": "Hanamkonda Fire Station",
                "contact": "101 / +91 870 257 7101",
                "unit_lead": "Lead Officer G. Venkatesh",
                "sector": "Warangal Industrial & Commercial Zone",
                "base_lat": 17.9950,
                "base_lon": 79.5750,
                "lat": 17.9950,
                "lon": 79.5750,
                "heading": 90.0,
                "speed_kmh": 0.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.9950, 79.5750),
                    (17.9850, 79.5880)
                ],
                "patrol_idx": 0
            },
            # Andhra Pradesh Units
            "RPU-AP-VZG": {
                "code": "RPU-AP-VZG",
                "name": "Visakhapatnam Coastal Police Patrol",
                "type": "POLICE",
                "department": "Visakhapatnam City Police Commissionerate",
                "department_station": "Beach Road Coastal Police Station, Vizag",
                "contact": "100 / +91 891 256 5454",
                "unit_lead": "Inspector V. Ramesh",
                "sector": "Visakhapatnam RK Beach & Marine Drive",
                "base_lat": 17.7126,
                "base_lon": 83.3241,
                "lat": 17.7126,
                "lon": 83.3241,
                "heading": 45.0,
                "speed_kmh": 35.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.7126, 83.3241),  # RK Beach
                    (17.7250, 83.3380),  # Kailasagiri Foothills
                    (17.6967, 83.2980),  # Port Area
                    (17.7050, 83.3150)
                ],
                "patrol_idx": 0
            },
            "FIRE-AP-VZG": {
                "code": "FIRE-AP-VZG",
                "name": "Vizag Marine & High-Capacity Fire Tender",
                "type": "FIRE",
                "department": "Andhra Pradesh State Disaster Response & Fire Services",
                "department_station": "Visakhapatnam Port Fire Station",
                "contact": "101 / +91 891 256 7101",
                "unit_lead": "Station Fire Officer D. Appa Rao",
                "sector": "Vizag Coastal Port & Industrial Zone",
                "base_lat": 17.7020,
                "base_lon": 83.2950,
                "lat": 17.7020,
                "lon": 83.2950,
                "heading": 135.0,
                "speed_kmh": 0.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (17.7020, 83.2950),
                    (17.7120, 83.3100)
                ],
                "patrol_idx": 0
            },
            "RPU-AP-BZA": {
                "code": "RPU-AP-BZA",
                "name": "Vijayawada City Police Interceptor",
                "type": "POLICE",
                "department": "Vijayawada City Police Commissionerate",
                "department_station": "Governorpet Police Station, Vijayawada",
                "contact": "100 / +91 866 257 4100",
                "unit_lead": "Inspector T. Srinivas",
                "sector": "Vijayawada MG Road / Benz Circle",
                "base_lat": 16.5062,
                "base_lon": 80.6480,
                "lat": 16.5062,
                "lon": 80.6480,
                "heading": 270.0,
                "speed_kmh": 32.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (16.5062, 80.6480),  # Benz Circle
                    (16.5090, 80.6200),  # PNBS Bus Terminal
                    (16.5180, 80.6350),  # Eluru Road
                    (16.4950, 80.6420)
                ],
                "patrol_idx": 0
            },
            "FIRE-AP-BZA": {
                "code": "FIRE-AP-BZA",
                "name": "Vijayawada Central Fire Brigade",
                "type": "FIRE",
                "department": "AP Fire Services - Krishna District",
                "department_station": "Kaleswara Rao Market Fire Station, Vijayawada",
                "contact": "101 / +91 866 242 0101",
                "unit_lead": "Fire Commander B. Mohan",
                "sector": "Vijayawada Metro Fire Zone",
                "base_lat": 16.5120,
                "base_lon": 80.6250,
                "lat": 16.5120,
                "lon": 80.6250,
                "heading": 60.0,
                "speed_kmh": 0.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (16.5120, 80.6250),
                    (16.5080, 80.6380)
                ],
                "patrol_idx": 0
            },
            "RPU-AP-TPT": {
                "code": "RPU-AP-TPT",
                "name": "Tirupati Pilgrim Safety Taskforce",
                "type": "POLICE",
                "department": "Tirupati Urban District Police",
                "department_station": "Alipiri Security Outpost Police Station",
                "contact": "100 / +91 877 228 7777",
                "unit_lead": "Deputy SP N. Bhaskar",
                "sector": "Tirupati Temple Foothills Zone",
                "base_lat": 13.6369,
                "base_lon": 79.4042,
                "lat": 13.6369,
                "lon": 79.4042,
                "heading": 15.0,
                "speed_kmh": 28.0,
                "status": "PATROLLING",
                "assigned_incident": None,
                "distance_to_target_km": 0.0,
                "eta_seconds": 0,
                "patrol_waypoints": [
                    (13.6369, 79.4042),
                    (13.6290, 79.4200),
                    (13.6450, 79.4120)
                ],
                "patrol_idx": 0
            }
        }

        # Initialize with baseline dispatch message
        self.messages.append({
            "id": f"MSG-CAD-{int(time.time()*1000)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "incident_id": 1,
            "incident_number": "INC-FE-SYS-INIT",
            "category": "CAD_SYSTEM_START",
            "severity": "NORMAL",
            "target_department": "Unified Emergency Services (Telangana & Andhra Pradesh)",
            "target_station": "State Command and Control Center (Banjara Hills)",
            "assigned_unit": "ALL_UNITS",
            "unit_lead": "Command Controller",
            "channel": "STATE CAD / TETRA RADIO SECURE GATEWAY",
            "message": "✓ Inter-agency emergency telemetry online. Patrolling police and fire units linked to real-time automated dispatch.",
            "status": "ONLINE"
        })

        # Start background simulation thread
        self.sim_thread = threading.Thread(target=self._run_simulation, daemon=True)
        self.sim_thread.start()

    def _run_simulation(self):
        """Continuously advances unit kinematics every 1.0 second."""
        while self.is_running:
            try:
                self._tick()
            except Exception:
                pass
            time.sleep(1.0)

    def _tick(self):
        """Advances patrol movement or en-route navigation towards assigned incident."""
        for code, u in self.units.items():
            if u["status"] == "PATROLLING":
                # Patrol around sector
                wps = u.get("patrol_waypoints", [])
                if not wps:
                    continue
                target_lat, target_lon = wps[u["patrol_idx"]]
                dist = haversine_km(u["lat"], u["lon"], target_lat, target_lon)
                if dist < 0.08:  # reached waypoint
                    u["patrol_idx"] = (u["patrol_idx"] + 1) % len(wps)
                    target_lat, target_lon = wps[u["patrol_idx"]]

                # Move slightly toward target patrol waypoint
                step = 0.00015  # ~15-20 meters per second (~50 km/h)
                d_lat = target_lat - u["lat"]
                d_lon = target_lon - u["lon"]
                mag = math.sqrt(d_lat*d_lat + d_lon*d_lon)
                if mag > 0:
                    u["lat"] += (d_lat / mag) * step
                    u["lon"] += (d_lon / mag) * step
                    u["heading"] = bearing_degrees(u["lat"] - (d_lat / mag) * step, u["lon"] - (d_lon / mag) * step, u["lat"], u["lon"])
                u["speed_kmh"] = round(28.0 + math.sin(time.time() * 0.1) * 6.0, 1)

            elif u["status"] == "DISPATCHED":
                # En route to incident location
                inc = u.get("assigned_incident")
                if not inc:
                    u["status"] = "PATROLLING"
                    continue

                target_lat = inc["target_lat"]
                target_lon = inc["target_lon"]
                dist = haversine_km(u["lat"], u["lon"], target_lat, target_lon)
                u["distance_to_target_km"] = dist

                # Emergency response speed: ~60 km/h (~0.0003 degrees per tick)
                step = 0.00030
                u["speed_kmh"] = 62.5
                u["eta_seconds"] = max(10, int((dist / 60.0) * 3600))

                if dist <= 0.05:  # within 50 meters -> Arrived at Scene!
                    u["status"] = "ON_SCENE"
                    u["speed_kmh"] = 0.0
                    u["distance_to_target_km"] = 0.0
                    u["eta_seconds"] = 0

                    # Emit arrival confirmation message
                    arrival_msg = {
                        "id": f"MSG-CAD-{int(time.time()*1000)}",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "incident_id": inc.get("incident_id"),
                        "incident_number": inc.get("incident_number"),
                        "category": inc.get("category"),
                        "severity": inc.get("severity", "HIGH"),
                        "target_department": u["department"],
                        "target_station": u["department_station"],
                        "assigned_unit": u["code"],
                        "unit_lead": u["unit_lead"],
                        "channel": "TETRA POLICE / FIRE OPERATIONAL FREQUENCY",
                        "message": (
                            f"✅ [ARRIVAL CONFIRMED - ON SCENE] Unit {u['code']} ({u['name']}) has ARRIVED at "
                            f"{inc.get('location_name', 'incident location')} [{u['lat']:.4f}, {u['lon']:.4f}]. "
                            f"Verified on site. Immediate perimeter securing & containment in progress."
                        ),
                        "status": "ARRIVED_ON_SCENE"
                    }
                    self.messages.insert(0, arrival_msg)

                else:
                    d_lat = target_lat - u["lat"]
                    d_lon = target_lon - u["lon"]
                    mag = math.sqrt(d_lat*d_lat + d_lon*d_lon)
                    if mag > 0:
                        u["lat"] += (d_lat / mag) * step
                        u["lon"] += (d_lon / mag) * step
                        u["heading"] = bearing_degrees(u["lat"] - (d_lat / mag) * step, u["lon"] - (d_lon / mag) * step, u["lat"], u["lon"])

    def get_live_units(self) -> List[Dict[str, Any]]:
        """Returns live kinematic state of all patrolling and responding units."""
        return list(self.units.values())

    def get_messages(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Returns recent inter-departmental CAD emergency messages."""
        return self.messages[:limit]

    def find_nearest_unit(self, lat: float, lon: float, unit_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Finds closest available or patrolling unit to given coordinates."""
        candidates = list(self.units.values())
        if unit_type:
            candidates = [u for u in candidates if u["type"].upper() == unit_type.upper()]
        if not candidates:
            candidates = list(self.units.values())

        best_unit = None
        best_dist = float("inf")
        for u in candidates:
            d = haversine_km(lat, lon, u["lat"], u["lon"])
            if d < best_dist:
                best_dist = d
                best_unit = u
        return best_unit

    def dispatch_unit_to_incident(
        self,
        team_code: str,
        incident_id: int,
        incident_number: str,
        title: str,
        category: str,
        severity: str,
        target_lat: float,
        target_lon: float,
        location_name: str
    ) -> Dict[str, Any]:
        """
        Dispatches a specific response unit to an incident.
        Automatically transmits alert message to respective police/fire department.
        """
        u = self.units.get(team_code)
        if not u:
            # Fallback to nearest unit
            u = self.find_nearest_unit(target_lat, target_lon)
            if not u:
                return {"status": "ERROR", "message": f"Unit {team_code} not found"}

        dist = haversine_km(u["lat"], u["lon"], target_lat, target_lon)
        eta_sec = max(15, int((dist / 60.0) * 3600))

        u["status"] = "DISPATCHED"
        u["distance_to_target_km"] = dist
        u["eta_seconds"] = eta_sec
        u["speed_kmh"] = 60.0
        u["assigned_incident"] = {
            "incident_id": incident_id,
            "incident_number": incident_number,
            "title": title,
            "category": category,
            "severity": severity,
            "target_lat": target_lat,
            "target_lon": target_lon,
            "location_name": location_name
        }

        # Transmit Official Departmental CAD / Radio Dispatch Message
        msg_payload = {
            "id": f"MSG-CAD-{int(time.time()*1000)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "incident_id": incident_id,
            "incident_number": incident_number,
            "category": category,
            "severity": severity,
            "target_department": u["department"],
            "target_station": u["department_station"],
            "assigned_unit": u["code"],
            "unit_lead": u["unit_lead"],
            "channel": "CAD COMPUTER-AIDED DISPATCH & TETRA RADIO GATEWAY",
            "message": (
                f"🚨 [URGENT DISPATCH ALERT TO {u['department_station'].upper()}]\n"
                f"Incident: {incident_number} — {title} ({category})\n"
                f"Location: {location_name} (Coordinates: {target_lat:.4f}°N, {target_lon:.4f}°E)\n"
                f"Priority Severity: {severity}\n"
                f"Assigned Unit: {u['code']} ({u['name']})\n"
                f"Status: Unit Dispatched. Initial ETA: {round(eta_sec / 60.0, 1)} minutes ({dist} km). Live GPS Tracking Engaged."
            ),
            "status": "DISPATCHED_EN_ROUTE"
        }
        self.messages.insert(0, msg_payload)

        return {
            "status": "SUCCESS",
            "message": f"🚨 Automated Alert Transmitted to {u['department_station']}. {u['code']} is en route to scene.",
            "unit": u,
            "dispatch_message": msg_payload
        }

    def reset_unit(self, team_code: str):
        """Resets a unit to baseline sector patrol."""
        u = self.units.get(team_code)
        if not u:
            return
        u["status"] = "PATROLLING"
        u["assigned_incident"] = None
        u["distance_to_target_km"] = 0.0
        u["eta_seconds"] = 0
        u["speed_kmh"] = 30.0

    def reset_all_units(self):
        """Resets all units back to their designated patrol routes."""
        for code in self.units.keys():
            self.reset_unit(code)


# Global singleton instance
responder_service = ResponderService()
