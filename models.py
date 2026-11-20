"""
FALCON EYE - Database ORM Models
Defines tables for USERS, CAMERAS, DRONES, INCIDENTS, DETECTIONS,
EVIDENCE, RESPONSE_TEAMS, RESPONSE_ASSIGNMENTS, AUDIT_LOGS, and CROWD_STATISTICS.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="OPERATOR", nullable=False)  # ADMIN, OPERATOR, RESPONDER, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="user")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_code = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    location_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    zone = Column(String(50), default="Central Plaza")  # e.g., North Gate, Metro Hub
    stream_type = Column(String(30), default="SIMULATED")  # RTSP, WEBCAM, SIMULATED, UPLOAD
    stream_url = Column(String(255), nullable=True)
    status = Column(String(30), default="ONLINE")  # ONLINE, OFFLINE, MAINTENANCE
    fps = Column(Float, default=30.0)
    resolution = Column(String(20), default="1920x1080")
    is_simulated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="camera")
    crowd_stats = relationship("CrowdStatistic", back_populates="camera")


class Drone(Base):
    __tablename__ = "drones"

    id = Column(Integer, primary_key=True, index=True)
    callsign = Column(String(50), unique=True, index=True, nullable=False)
    model = Column(String(100), default="Falcon-SkyScout-X4")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=65.0)  # meters
    speed = Column(Float, default=28.5)     # km/h
    battery = Column(Float, default=94.0)   # percentage
    heading = Column(Float, default=145.0)  # compass degrees
    status = Column(String(30), default="PATROLLING")  # IDLE, PATROLLING, RESPONDING, RETURNING
    target_zone = Column(String(100), default="Metro Transit Junction")
    stream_url = Column(String(255), nullable=True)
    is_simulation = Column(Boolean, default=True)
    last_ping = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="drone")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    # Categories: CROWD_CONGESTION, FIRE_SMOKE, TRAFFIC_COLLISION, FALLEN_PERSON, HAZARD, SUSPICIOUS_ACTIVITY

    severity = Column(String(20), default="MEDIUM", index=True)
    # Severity: CRITICAL, HIGH, MEDIUM, LOW

    status = Column(String(30), default="DETECTED", index=True)
    # Lifecycle: DETECTED -> PENDING_REVIEW -> VERIFIED -> ACKNOWLEDGED -> ASSIGNED -> RESOLVED

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(150), nullable=False)

    confidence = Column(Float, default=0.85)
    source_type = Column(String(30), default="CAMERA")  # CAMERA, DRONE, CITIZEN_REPORT, AI_SYSTEM
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    drone_id = Column(Integer, ForeignKey("drones.id"), nullable=True)

    risk_score = Column(Float, default=50.0)  # 0 to 100
    risk_factors = Column(Text, nullable=True)  # JSON string or description of contributing factors

    description = Column(Text, nullable=True)
    original_language = Column(String(10), default="en")
    translated_description = Column(Text, nullable=True)

    evidence_image_path = Column(String(255), nullable=True)
    evidence_hash = Column(String(64), nullable=True)  # SHA-256 integrity hash

    verified_by = Column(String(100), nullable=True)
    verification_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    camera = relationship("Camera", back_populates="incidents")
    drone = relationship("Drone", back_populates="incidents")
    detections = relationship("Detection", back_populates="incident", cascade="all, delete-orphan")
    evidence_records = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    assignments = relationship("ResponseAssignment", back_populates="incident", cascade="all, delete-orphan")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    object_class = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    bbox = Column(String(100), nullable=False)  # x1,y1,x2,y2
    source_label = Column(String(100), nullable=True)
    frame_index = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="detections")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(20), default="IMAGE")  # IMAGE, VIDEO, AUDIO, LOG
    file_hash = Column(String(64), nullable=False)   # SHA-256 hash
    captured_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String(255), nullable=True)
    is_sensitive = Column(Boolean, default=False)
    retention_days = Column(Integer, default=30)

    incident = relationship("Incident", back_populates="evidence_records")


class ResponseTeam(Base):
    __tablename__ = "response_teams"

    id = Column(Integer, primary_key=True, index=True)
    team_code = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    team_type = Column(String(30), nullable=False)  # POLICE, FIRE, MEDICAL, TRAFFIC, DISASTER_MGMT
    contact_number = Column(String(30), nullable=False)
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    base_location = Column(String(150), nullable=False)
    status = Column(String(30), default="AVAILABLE")  # AVAILABLE, DISPATCHED, ON_SCENE, BUSY
    unit_lead = Column(String(100), default="Commander")

    assignments = relationship("ResponseAssignment", back_populates="team")


class ResponseAssignment(Base):
    __tablename__ = "response_assignments"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("response_teams.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    arrival_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="assignments")
    team = relationship("ResponseTeam", back_populates="assignments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(50), default="SYSTEM")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # INCIDENT, USER, DRONE, CAMERA, EVIDENCE
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")


class CrowdStatistic(Base):
    __tablename__ = "crowd_statistics"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    zone = Column(String(50), nullable=False)
    people_count = Column(Integer, nullable=False)
    density_level = Column(String(20), default="GREEN")  # GREEN, YELLOW, ORANGE, RED
    threshold_limit = Column(Integer, default=30)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    camera = relationship("Camera", back_populates="crowd_stats")
