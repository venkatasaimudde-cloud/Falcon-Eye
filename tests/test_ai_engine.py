"""
Unit Tests for FALCON EYE AI Computer Vision Engines
"""

import os
import sys
import cv2
import numpy as np
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.ai.detector import detector
from backend.ai.crowd_analyzer import crowd_analyzer
from backend.ai.fire_smoke_detector import fire_smoke_detector
from backend.ai.face_privacy import face_privacy_engine
from backend.ai.hazard_detector import hazard_detector
from backend.ai.risk_engine import risk_engine


def test_yolo_detector():
    sample_path = os.path.join(BASE_DIR, "sample_data", "sample_crowd.jpg")
    assert os.path.exists(sample_path), "Sample crowd image should exist"
    
    img = cv2.imread(sample_path)
    annotated, detections, counts = detector.detect_frame(img, conf_threshold=0.25)
    
    assert annotated is not None
    assert isinstance(detections, list)
    assert isinstance(counts, dict)


def test_crowd_analyzer():
    # 1. Density classification
    lvl, hex_c, msg = crowd_analyzer.classify_density(10)
    assert lvl == "GREEN"

    lvl, hex_c, msg = crowd_analyzer.classify_density(35)
    assert lvl == "ORANGE"

    lvl, hex_c, msg = crowd_analyzer.classify_density(60)
    assert lvl == "RED"

    # 2. Pedestrian tracking & ID assignment
    crowd_analyzer.reset_tracker()
    boxes_f1 = [[50, 50, 80, 120], [100, 100, 130, 170]]
    tracks_f1 = crowd_analyzer.update_tracks(boxes_f1)
    assert len(tracks_f1) == 2
    assert tracks_f1[0].track_id == 1
    assert tracks_f1[1].track_id == 2
    assert len(crowd_analyzer.cumulative_unique_ids) == 2

    # Frame 2: Pedestrians move slightly (tracking continuity)
    boxes_f2 = [[54, 53, 84, 123], [105, 98, 135, 168]]
    tracks_f2 = crowd_analyzer.update_tracks(boxes_f2)
    assert len(tracks_f2) == 2
    assert tracks_f2[0].track_id == 1
    assert tracks_f2[1].track_id == 2
    # Verify no duplicate unique IDs created for existing people
    assert len(crowd_analyzer.cumulative_unique_ids) == 2

    # 3. Gaussian KDE Heatmap generation
    heatmap = crowd_analyzer.generate_gaussian_kde_heatmap((480, 640), boxes_f2)
    assert heatmap is not None
    assert heatmap.shape == (480, 640, 3)

    # 4. Perspective-calibrated Zone Analysis
    zone_results = crowd_analyzer.analyze_zones((480, 640), tracks_f2)
    assert isinstance(zone_results, list)
    assert len(zone_results) >= 2
    for z in zone_results:
        assert "density_p_m2" in z
        assert "calibrated_area_m2" in z
        assert "los_label" in z

    # 5. Movement and Anomaly Analysis
    movement = crowd_analyzer.analyze_movement(tracks_f2)
    assert "dominant_direction" in movement
    assert "average_speed_px_s" in movement
    assert "bottleneck_detected" in movement

    # 6. Full overlay pipeline
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    annotated, summary = crowd_analyzer.overlay_crowd_analytics(dummy_frame, boxes_f2)
    assert annotated is not None
    assert summary["active_count"] == 2
    assert summary["cumulative_unique_visitors"] == 2



def test_fire_smoke_detector():
    sample_path = os.path.join(BASE_DIR, "sample_data", "sample_fire.jpg")
    assert os.path.exists(sample_path), "Sample fire image should exist"

    img = cv2.imread(sample_path)
    annotated, result = fire_smoke_detector.analyze_frame(img)

    assert annotated is not None
    assert "fire_detected" in result
    assert "fire_confidence" in result
    assert result["fire_detected"] is True, "Fire should be detected in synthetic fire sample"


def test_face_privacy_engine():
    dummy = np.zeros((200, 200, 3), dtype=np.uint8)
    processed, records, stats = face_privacy_engine.detect_and_protect(dummy, blur_faces=True)

    assert processed is not None
    assert stats["privacy_mode"] == "ANONYMIZED_BLUR"

    # Test consent-based staff registry
    auth_check = face_privacy_engine.verify_authorized_personnel("FE-SEC-091")
    assert auth_check["matched"] is True
    assert "Vikram Sharma" in auth_check["message"]


def test_risk_engine():
    risk = risk_engine.evaluate_situational_risk(crowd_count=45, active_incidents_in_zone=1, has_fire_smoke=True)
    assert risk["risk_score"] > 60
    assert risk["risk_category"] in ["HIGH", "CRITICAL"]
    assert len(risk["contributing_factors"]) > 0
