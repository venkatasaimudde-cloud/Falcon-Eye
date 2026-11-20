"""
Unit and Integration Tests for Falcon Eye Cinematic 3D Eagle Flight Intro
Verifies:
1. Audio assets presence and validity (authentic eagle call, impacts, wing flaps, wind)
2. High-definition eagle visual assets presence
3. Three.js and GSAP runtime libraries
4. HTML markup integration in index.html and frontend/index.html
5. Prohibition of unwanted controls (no skip intro, no sound toggle, no replay button)
6. JavaScript orchestration logic and kinematic stages
"""

import os
import re
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
AUDIO_DIR = os.path.join(FRONTEND_DIR, "assets", "audio")
IMAGES_DIR = os.path.join(FRONTEND_DIR, "assets", "images")
JS_DIR = os.path.join(FRONTEND_DIR, "js")
CSS_DIR = os.path.join(FRONTEND_DIR, "css")


def test_audio_assets_exist_and_valid():
    """Verify all required audio assets exist and have substantial file size (> 10KB)."""
    required_audio = [
        "bald_eagle_call.mp3",
        "eagle_screech_short.mp3",
        "cinematic_impact.wav",
        "wing_flap.wav",
        "wind_ambience.wav",
    ]
    for audio_name in required_audio:
        path = os.path.join(AUDIO_DIR, audio_name)
        assert os.path.exists(path), f"Required audio asset missing: {audio_name}"
        size = os.path.getsize(path)
        assert size > 10000, f"Audio file {audio_name} is too small ({size} bytes)"


def test_eagle_image_assets_exist():
    """Verify photorealistic eagle textures and macro assets exist."""
    required_images = [
        "eagle_flight.jpg",
        "eagle_closeup.jpg",
        "eagle_pupil_vortex.jpg",
    ]
    for img_name in required_images:
        path = os.path.join(IMAGES_DIR, img_name)
        assert os.path.exists(path), f"Required image asset missing: {img_name}"
        size = os.path.getsize(path)
        assert size > 50000, f"Image asset {img_name} is too small ({size} bytes)"


def test_local_three_and_gsap_libraries():
    """Verify local three.min.js and gsap.min.js are available."""
    three_path = os.path.join(JS_DIR, "three.min.js")
    gsap_path = os.path.join(JS_DIR, "gsap.min.js")
    assert os.path.exists(three_path), "three.min.js missing from frontend/js"
    assert os.path.exists(gsap_path), "gsap.min.js missing from frontend/js"
    assert os.path.getsize(three_path) > 100000
    assert os.path.getsize(gsap_path) > 30000


def test_html_markup_integration():
    """Verify index.html and frontend/index.html have the intro container, canvas, and gateway."""
    for filename in ["index.html", os.path.join("frontend", "index.html")]:
        file_path = os.path.join(BASE_DIR, filename)
        assert os.path.exists(file_path), f"{filename} not found"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "cinematic_intro.css" in content, f"{filename} missing cinematic_intro.css"
        assert 'id="falcon-cinematic-intro"' in content, f"{filename} missing intro container"
        assert 'id="intro-webgl-canvas"' in content, f"{filename} missing webgl canvas"
        assert 'id="enter-falcon-btn"' in content, f"{filename} missing enter falcon button"
        assert 'id="intro-title-overlay"' in content, f"{filename} missing title overlay"
        assert "cinematic_intro.js" in content, f"{filename} missing cinematic_intro.js"


def test_prohibited_controls_removed():
    """Verify that skip intro, sound toggle, and replay buttons are NOT displayed."""
    for filename in ["index.html", os.path.join("frontend", "index.html")]:
        file_path = os.path.join(BASE_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Prohibited controls
        assert "skip-intro" not in content.lower(), f"Prohibited skip intro control found in {filename}"
        assert "sound-toggle" not in content.lower(), f"Prohibited sound toggle control found in {filename}"
        assert "audio-preview" not in content.lower(), f"Prohibited audio preview control found in {filename}"
        assert "replay-intro" not in content.lower(), f"Prohibited replay intro control found in {filename}"


def test_cinematic_intro_js_logic():
    """Verify cinematic_intro.js implements all key animation and audio phases."""
    intro_js_path = os.path.join(JS_DIR, "cinematic_intro.js")
    assert os.path.exists(intro_js_path), "cinematic_intro.js missing"
    with open(intro_js_path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Sound system & authentic eagle call
    assert "bald_eagle_call.mp3" in code
    assert "cinematicImpact" in code
    assert "wingFlap" in code
    assert "windAmbience" in code

    # 2. Eagle 3D anatomy
    assert "buildEagleModel" in code
    assert "headNeckGroup" in code
    assert "lowerBeak" in code
    assert "leftWing" in code and "rightWing" in code
    assert "primaryFeathers" in code or "leftPrimaries" in code

    # 3. Flapping kinematics & Beak sync
    assert "updateEagleKinematics" in code
    assert "beakOpen" in code
    assert "FlightState" in code

    # 4. Cinematic Timeline phases
    assert "startCinematicTimeline" in code
    assert "hyperspaceParticles" in code
    assert "title-active" in code
    assert "launchFalconEyeExperience" in code
