"""
FALCON EYE - Database Initialization & Seed Script
Populates the database with initial users, cameras, drones, response teams,
incidents, and crowd telemetry across Telangana & Andhra Pradesh state grid.
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import engine, Base, SessionLocal
from backend.models import User, Camera, Drone, ResponseTeam, Incident, CrowdStatistic, AuditLog
from backend.auth import hash_password


def seed_database(force_refresh: bool = False):
    print("[*] Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    if force_refresh:
        print("[*] Refreshing seed data across Telangana & Andhra Pradesh...")
        db.query(AuditLog).delete()
        db.query(CrowdStatistic).delete()
        db.query(Incident).delete()
        db.query(ResponseTeam).delete()
        db.query(Drone).delete()
        db.query(Camera).delete()
        db.commit()

    # 1. Seed Users
    if db.query(User).count() == 0:
        print("[*] Seeding default authorized users...")
        users = [
            User(
                username="admin",
                email="admin@falconeye.gov.in",
                full_name="Chief Controller Rajesh Varma",
                hashed_password=hash_password("falcon123"),
                role="ADMIN"
            ),
            User(
                username="operator",
                email="operator@falconeye.gov.in",
                full_name="Lead Operator Vikram Sharma",
                hashed_password=hash_password("falcon123"),
                role="OPERATOR"
            ),
            User(
                username="responder",
                email="responder@falconeye.gov.in",
                full_name="Field Commander Priya Reddy",
                hashed_password=hash_password("falcon123"),
                role="RESPONDER"
            ),
            User(
                username="viewer",
                email="viewer@falconeye.gov.in",
                full_name="City Auditor K. Murthy",
                hashed_password=hash_password("falcon123"),
                role="VIEWER"
            )
        ]
        db.add_all(users)
        db.commit()

    # 2. Seed Cameras across Telangana & Andhra Pradesh
    if db.query(Camera).count() == 0:
        print("[*] Seeding surveillance cameras across Telangana & Andhra Pradesh...")
        cameras = [
            # Telangana Cameras
            Camera(
                camera_code="CAM-TG-HYD-01",
                name="Central Plaza CCTV Alpha",
                location_name="Hyderabad Central Transit Plaza",
                latitude=17.3850,
                longitude=78.4867,
                zone="Hyderabad Metro",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-TG-HYD-02",
                name="Charminar Market Square",
                location_name="Historic Bazaar Corridor, Hyderabad",
                latitude=17.3616,
                longitude=78.4747,
                zone="Hyderabad Metro",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=25.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-TG-HYD-03",
                name="Hitec City Cyber Corridor",
                location_name="Cyber Towers Intersection, Gachibowli",
                latitude=17.4504,
                longitude=78.3808,
                zone="Hyderabad Cyberabad",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-TG-WGL-01",
                name="Warangal Kazipet Junction",
                location_name="Railway Station & Bus Plaza, Warangal",
                latitude=17.9784,
                longitude=79.5041,
                zone="Telangana North-East",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-TG-KRM-01",
                name="Karimnagar Collectorate Chowk",
                location_name="Administrative Center, Karimnagar",
                latitude=18.4386,
                longitude=79.1288,
                zone="Telangana North",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-TG-NZB-01",
                name="Nizamabad Central Bus Square",
                location_name="Main Depot Interchange, Nizamabad",
                latitude=18.6725,
                longitude=78.0941,
                zone="Telangana West",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),

            # Andhra Pradesh Cameras
            Camera(
                camera_code="CAM-AP-VZG-01",
                name="Visakhapatnam RK Beach Promenade",
                location_name="Coastal Seafront Plaza, Visakhapatnam",
                latitude=17.7126,
                longitude=83.3241,
                zone="AP Coastal Zone",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-AP-VZG-02",
                name="Visakhapatnam Port Road",
                location_name="Harbor Marine Freight Corridor, Vizag",
                latitude=17.6967,
                longitude=83.2980,
                zone="AP Port Zone",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-AP-BZA-01",
                name="Vijayawada PNBS Terminal",
                location_name="Pandit Nehru Interstate Bus Station, Vijayawada",
                latitude=16.5090,
                longitude=80.6200,
                zone="AP Capital Region",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-AP-BZA-02",
                name="Vijayawada Benz Circle",
                location_name="Arterial Ring Road Junction, Vijayawada",
                latitude=16.5005,
                longitude=80.6520,
                zone="AP Capital Region",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-AP-GNT-01",
                name="Guntur Market Corridor",
                location_name="Central Commercial Yard, Guntur",
                latitude=16.3067,
                longitude=80.4365,
                zone="AP South-Central",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-AP-TPT-01",
                name="Tirupati Alipiri Checkpost",
                location_name="Hill Foot Entrance Security Corridor, Tirupati",
                latitude=13.6500,
                longitude=79.3900,
                zone="AP Rayalaseema",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            ),
            Camera(
                camera_code="CAM-AP-KNL-01",
                name="Kurnool Rajvihar Circle",
                location_name="City Center Square, Kurnool",
                latitude=15.8281,
                longitude=78.0373,
                zone="AP Rayalaseema",
                stream_type="SIMULATED",
                status="ONLINE",
                fps=30.0,
                is_simulated=True
            )
        ]
        db.add_all(cameras)
        db.commit()

    # 3. Seed Drones
    if db.query(Drone).count() == 0:
        print("[*] Seeding simulated UAV drones...")
        drones = [
            Drone(
                callsign="FALCON-UAV-ALPHA-1",
                model="Falcon SkyScout-X4 Quad-Rotor",
                latitude=17.3850,
                longitude=78.4867,
                altitude=65.0,
                speed=28.5,
                battery=94.0,
                heading=145.0,
                status="PATROLLING",
                target_zone="Telangana Corridor (Hyderabad)",
                is_simulation=True
            ),
            Drone(
                callsign="FALCON-UAV-BETA-2",
                model="Falcon AeroGuard-VTOL Long-Range",
                latitude=17.7126,
                longitude=83.3241,
                altitude=90.0,
                speed=36.0,
                battery=88.5,
                heading=210.0,
                status="PATROLLING",
                target_zone="Andhra Pradesh Coastal Corridor (Vizag)",
                is_simulation=True
            )
        ]
        db.add_all(drones)
        db.commit()

    # 4. Seed Response Teams across Telangana & Andhra Pradesh
    if db.query(ResponseTeam).count() == 0:
        print("[*] Seeding emergency response teams...")
        teams = [
            ResponseTeam(
                team_code="RPU-TG-01",
                name="Rapid Police Patrol Unit 01 (Hyderabad)",
                team_type="POLICE",
                contact_number="100 / +91 40 2785 2400",
                current_latitude=17.3860,
                current_longitude=78.4850,
                base_location="Hyderabad Police Commissionerate",
                status="AVAILABLE",
                unit_lead="Inspector K. Naidu"
            ),
            ResponseTeam(
                team_code="MED-TG-01",
                name="Medical Trauma Ambulance 01 (Hyderabad)",
                team_type="MEDICAL",
                contact_number="108 / +91 40 2460 0146",
                current_latitude=17.3790,
                current_longitude=78.4760,
                base_location="Osmania General Hospital",
                status="AVAILABLE",
                unit_lead="Dr. S. Kulkarni"
            ),
            ResponseTeam(
                team_code="FIRE-TG-01",
                name="Central Fire & Rescue Tender (Hyderabad)",
                team_type="FIRE",
                contact_number="101 / +91 40 2344 2944",
                current_latitude=17.3630,
                current_longitude=78.4760,
                base_location="Moghalpura Fire Station",
                status="AVAILABLE",
                unit_lead="Station Officer R. Singh"
            ),
            ResponseTeam(
                team_code="RPU-TG-WGL",
                name="Warangal Quick Reaction Patrol",
                team_type="POLICE",
                contact_number="100 / +91 870 244 4250",
                current_latitude=17.9700,
                current_longitude=79.5900,
                base_location="Warangal City Police HQ",
                status="AVAILABLE",
                unit_lead="Sub-Inspector M. Goud"
            ),
            ResponseTeam(
                team_code="RPU-AP-VZG",
                name="Visakhapatnam Coastal Patrol Unit",
                team_type="POLICE",
                contact_number="100 / +91 891 256 5454",
                current_latitude=17.7100,
                current_longitude=83.3200,
                base_location="Vizag Beach Road Police Station",
                status="AVAILABLE",
                unit_lead="Inspector V. Ramesh"
            ),
            ResponseTeam(
                team_code="MED-AP-VZG",
                name="KGH Emergency Trauma Ambulance",
                team_type="MEDICAL",
                contact_number="108 / +91 891 256 4891",
                current_latitude=17.7090,
                current_longitude=83.3060,
                base_location="King George Hospital Vizag",
                status="AVAILABLE",
                unit_lead="Dr. P. Swaroop"
            ),
            ResponseTeam(
                team_code="RPU-AP-BZA",
                name="Vijayawada Metro Police Patrol",
                team_type="POLICE",
                contact_number="100 / +91 866 257 4100",
                current_latitude=16.5080,
                current_longitude=80.6400,
                base_location="Vijayawada Police Commissionerate",
                status="AVAILABLE",
                unit_lead="Inspector T. Srinivas"
            ),
            ResponseTeam(
                team_code="RPU-AP-TPT",
                name="Tirupati Pilgrim Safety Taskforce",
                team_type="POLICE",
                contact_number="100 / +91 877 228 7777",
                current_latitude=13.6300,
                current_longitude=79.4100,
                base_location="Alipiri Security Command Hub",
                status="AVAILABLE",
                unit_lead="Inspector G. Reddy"
            )
        ]
        db.add_all(teams)
        db.commit()

    # 5. Seed Real-world Incidents across Telangana & Andhra Pradesh
    if db.query(Incident).count() == 0:
        print("[*] Seeding realistic sample incidents across Telangana & Andhra Pradesh...")
        now = datetime.utcnow()
        incidents = [
            Incident(
                incident_number="INC-FE-20261119-001",
                title="Dense Pedestrian Surge at Metro Exit",
                category="CROWD_CONGESTION",
                severity="HIGH",
                status="VERIFIED",
                latitude=17.3895,
                longitude=78.4890,
                location_name="Metro Station Entry Gate 3, Hyderabad (Telangana)",
                source_type="CAMERA",
                camera_id=1,
                confidence=0.88,
                risk_score=68.0,
                created_at=now - timedelta(minutes=45),
                acknowledged_at=now - timedelta(minutes=40),
                description="Pedestrian density reached 38 persons in the transit funnel. Flow rate is severely restricted."
            ),
            Incident(
                incident_number="INC-FE-20261119-002",
                title="Two-Wheeler & Auto-Rickshaw Collision",
                category="TRAFFIC_COLLISION",
                severity="MEDIUM",
                status="ASSIGNED",
                latitude=17.4010,
                longitude=78.4780,
                location_name="Arterial Ring Road Intersection, Hyderabad (Telangana)",
                source_type="CAMERA",
                camera_id=3,
                confidence=0.81,
                risk_score=52.0,
                created_at=now - timedelta(minutes=28),
                acknowledged_at=now - timedelta(minutes=24),
                description="Minor vehicular impact with debris on roadway. Response team RPU-TG-01 dispatched."
            ),
            Incident(
                incident_number="INC-FE-20261119-003",
                title="Heavy Gathering at Bhadrakali Temple Festival",
                category="CROWD_CONGESTION",
                severity="HIGH",
                status="VERIFIED",
                latitude=17.9820,
                longitude=79.5900,
                location_name="Bhadrakali Temple Ghats, Warangal (Telangana)",
                source_type="CAMERA",
                camera_id=4,
                confidence=0.85,
                risk_score=64.0,
                created_at=now - timedelta(minutes=18),
                acknowledged_at=now - timedelta(minutes=15),
                description="Festival congregation exceeding 45 people per sector. Monitoring crowd surge."
            ),
            Incident(
                incident_number="INC-FE-20261119-004",
                title="Coastal High Tide & Beachfront Crowd Advisory",
                category="HAZARD",
                severity="HIGH",
                status="VERIFIED",
                latitude=17.7130,
                longitude=83.3250,
                location_name="RK Beach Promenade, Visakhapatnam (Andhra Pradesh)",
                source_type="CAMERA",
                camera_id=7,
                confidence=0.92,
                risk_score=74.0,
                created_at=now - timedelta(minutes=35),
                acknowledged_at=now - timedelta(minutes=30),
                description="Unusual wave surges along the promenade. Public safety alert issued for shoreline clearance."
            ),
            Incident(
                incident_number="INC-FE-20261119-005",
                title="High Traffic Gridlock at Benz Circle",
                category="TRAFFIC_COLLISION",
                severity="MEDIUM",
                status="ASSIGNED",
                latitude=16.5005,
                longitude=80.6520,
                location_name="Benz Circle Intersection, Vijayawada (Andhra Pradesh)",
                source_type="CAMERA",
                camera_id=10,
                confidence=0.86,
                risk_score=58.0,
                created_at=now - timedelta(minutes=15),
                acknowledged_at=now - timedelta(minutes=12),
                description="Multi-lane traffic slowdown. Vijayawada Metro Police RPU-AP-BZA deployed to direct flow."
            ),
            Incident(
                incident_number="INC-FE-20261119-006",
                title="Pilgrim Footfall Surge at Alipiri Gate",
                category="CROWD_CONGESTION",
                severity="HIGH",
                status="VERIFIED",
                latitude=13.6520,
                longitude=79.3910,
                location_name="Alipiri Foothills Entrance, Tirupati (Andhra Pradesh)",
                source_type="CAMERA",
                camera_id=12,
                confidence=0.90,
                risk_score=71.0,
                created_at=now - timedelta(minutes=50),
                acknowledged_at=now - timedelta(minutes=42),
                description="Weekend pilgrimage rush. Steady movement maintained through queue barricades."
            )
        ]
        db.add_all(incidents)
        db.commit()

    # 6. Seed Crowd Statistics for Charts
    if db.query(CrowdStatistic).count() == 0:
        print("[*] Seeding historical crowd statistics...")
        stats = []
        now = datetime.utcnow()
        for i in range(12):
            t = now - timedelta(minutes=(11 - i) * 10)
            count = 14 + (i * 3) if i < 7 else 38 - ((i - 7) * 2)
            dens = "GREEN" if count < 15 else "YELLOW" if count <= 30 else "ORANGE" if count <= 50 else "RED"
            stats.append(
                CrowdStatistic(
                    camera_id=1,
                    zone="Central Plaza Corridor",
                    people_count=count,
                    density_level=dens,
                    threshold_limit=30,
                    timestamp=t
                )
            )
        db.add_all(stats)
        db.commit()

    db.close()
    print("[+] Database initialization complete. State-wide coverage ready.")


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force_refresh=force)
