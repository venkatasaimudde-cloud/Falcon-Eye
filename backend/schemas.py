"""
FALCON EYE - Pydantic Schemas
Validation schemas for API requests and responses.
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = "OPERATOR"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


# Camera Schemas
class CameraBase(BaseModel):
    camera_code: str
    name: str
    location_name: str
    latitude: float
    longitude: float
    zone: str = "Central Plaza"
    stream_type: str = "SIMULATED"
    stream_url: Optional[str] = None
    status: str = "ONLINE"
    fps: float = 30.0
    resolution: str = "1920x1080"
    is_simulated: bool = True


class CameraResponse(CameraBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Drone Schemas
class DroneBase(BaseModel):
    callsign: str
    model: str = "Falcon-SkyScout-X4"
    latitude: float
    longitude: float
    altitude: float = 65.0
    speed: float = 28.5
    battery: float = 94.0
    heading: float = 145.0
    status: str = "PATROLLING"
    target_zone: str = "Metro Transit Junction"
    is_simulation: bool = True


class DroneResponse(DroneBase):
    id: int
    last_ping: datetime

    class Config:
        from_attributes = True


# Detection Schemas
class DetectionItem(BaseModel):
    object_class: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    source_label: Optional[str] = None


class DetectionResponse(BaseModel):
    id: int
    incident_id: Optional[int] = None
    object_class: str
    confidence: float
    bbox: str
    source_label: Optional[str] = None
    frame_index: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Incident Schemas
class IncidentCreate(BaseModel):
    title: str
    category: str
    severity: str = "MEDIUM"
    latitude: float
    longitude: float
    location_name: str
    confidence: float = 0.85
    source_type: str = "AI_SYSTEM"
    camera_id: Optional[int] = None
    drone_id: Optional[int] = None
    risk_score: float = 50.0
    risk_factors: Optional[str] = None
    description: Optional[str] = None
    evidence_image_path: Optional[str] = None
    evidence_hash: Optional[str] = None


class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    verified_by: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    incident_number: str
    title: str
    category: str
    severity: str
    status: str
    latitude: float
    longitude: float
    location_name: str
    confidence: float
    source_type: str
    camera_id: Optional[int] = None
    drone_id: Optional[int] = None
    risk_score: float
    risk_factors: Optional[str] = None
    description: Optional[str] = None
    original_language: Optional[str] = "en"
    translated_description: Optional[str] = None
    evidence_image_path: Optional[str] = None
    evidence_hash: Optional[str] = None
    verified_by: Optional[str] = None
    verification_notes: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# Response Team Schemas
class ResponseTeamBase(BaseModel):
    team_code: str
    name: str
    team_type: str
    contact_number: str
    current_latitude: float
    current_longitude: float
    base_location: str
    status: str = "AVAILABLE"
    unit_lead: str = "Commander"


class ResponseTeamResponse(ResponseTeamBase):
    id: int

    class Config:
        from_attributes = True


# Assign Team Schema
class AssignTeamRequest(BaseModel):
    incident_id: int
    team_id: int
    notes: Optional[str] = None


# Multilingual Report Schema
class MultilingualReportRequest(BaseModel):
    text: str
    language: str  # te (Telugu), hi (Hindi), en (English)
    location_name: Optional[str] = "Citizen Location"
    latitude: Optional[float] = 17.3850
    longitude: Optional[float] = 78.4867
    contact_number: Optional[str] = None


# Dashboard Stats
class DashboardStats(BaseModel):
    total_incidents: int
    active_incidents: int
    resolved_incidents: int
    people_detected: int
    vehicles_detected: int
    crowd_alerts: int
    fire_smoke_alerts: int
    monitored_sources: int
    drone_status: str
    drone_battery: float
    avg_ack_time_minutes: float
    system_health: str = "OPTIMAL (99.8%)"
