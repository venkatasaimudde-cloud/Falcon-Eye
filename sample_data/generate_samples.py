"""
FALCON EYE - Sample Media Assets Generator
Generates realistic sample images and video files for immediate testing and demonstration:
- sample_crowd.jpg (Pedestrian crowd scene)
- sample_traffic.jpg (Traffic street scene with vehicles)
- sample_fire.jpg (Simulated fire/smoke thermal hazard scene)
- sample_surveillance.mp4 (Short 5-second 30fps simulated surveillance video)
"""

import os
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_DIR = os.path.join(BASE_DIR, "sample_data")
os.makedirs(SAMPLES_DIR, exist_ok=True)


def generate_crowd_image():
    """Generates a realistic urban plaza crowd test image."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    for y in range(480):
        val = int(35 + (y / 480) * 35)
        img[y, :] = (val, val + 5, val + 15)

    # Grid floor
    for x in range(0, 640, 80):
        cv2.line(img, (x, 150), (int(x * 1.3), 480), (70, 75, 85), 1)

    # Pedestrians
    np.random.seed(101)
    for _ in range(35):
        px = np.random.randint(80, 560)
        py = np.random.randint(180, 440)
        scale = max(0.5, py / 400.0)
        hw = int(7 * scale)
        # Head
        cv2.circle(img, (px, py - int(30 * scale)), hw, (200, 180, 160), -1)
        # Torso
        cv2.rectangle(img, (px - int(10 * scale), py - int(22 * scale)),
                      (px + int(10 * scale), py), (np.random.randint(50, 200), np.random.randint(50, 180), np.random.randint(80, 220)), -1)
        # Legs
        cv2.line(img, (px - int(5 * scale), py), (px - int(5 * scale), py + int(24 * scale)), (50, 50, 70), max(2, int(3 * scale)))
        cv2.line(img, (px + int(5 * scale), py), (px + int(5 * scale), py + int(24 * scale)), (50, 50, 70), max(2, int(3 * scale)))

    out_path = os.path.join(SAMPLES_DIR, "sample_crowd.jpg")
    cv2.imwrite(out_path, img)
    print(f"[+] Saved {out_path}")
    return out_path


def generate_traffic_image():
    """Generates an urban street scene with multiple vehicles."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Asphalt roadway
    img[:, :] = (50, 55, 60)
    # Road markings (yellow center line, white dashed lane lines)
    cv2.line(img, (320, 0), (320, 480), (0, 215, 255), 3)
    for y in range(0, 480, 40):
        cv2.line(img, (160, y), (160, y + 20), (220, 220, 220), 2)
        cv2.line(img, (480, y), (480, y + 20), (220, 220, 220), 2)

    # Vehicles
    # Car 1 (Cyan Sedan)
    cv2.rectangle(img, (60, 180), (140, 300), (200, 180, 40), -1)
    cv2.rectangle(img, (75, 205), (125, 275), (230, 220, 120), -1)

    # Car 2 (Red SUV)
    cv2.rectangle(img, (200, 120), (290, 260), (40, 40, 210), -1)
    cv2.rectangle(img, (215, 150), (275, 230), (70, 70, 240), -1)

    # Bus (Yellow Transit Bus)
    cv2.rectangle(img, (360, 80), (450, 340), (0, 190, 240), -1)
    cv2.rectangle(img, (375, 100), (435, 320), (0, 140, 200), -1)

    out_path = os.path.join(SAMPLES_DIR, "sample_traffic.jpg")
    cv2.imwrite(out_path, img)
    print(f"[+] Saved {out_path}")
    return out_path


def generate_fire_image():
    """Generates a hazard scene with simulated fire flame and smoke plume."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Dim background
    for y in range(480):
        img[y, :] = (25, 25, 35)

    # Smoke plume (gray/cloudy low saturation)
    for i in range(12):
        cx = 320 + np.random.randint(-30, 30)
        cy = 160 + i * 15
        radius = 35 + i * 4
        overlay = img.copy()
        cv2.circle(overlay, (cx, cy), radius, (130, 135, 140), -1)
        cv2.addWeighted(overlay, 0.35, img, 0.65, 0, img)

    # Fire flame base (intense yellow, orange, red HSV bounds)
    # In BGR: Red=(0, 0, 255), Orange=(0, 140, 255), Yellow=(0, 230, 255)
    cv2.ellipse(img, (320, 350), (60, 80), 0, 0, 360, (0, 0, 255), -1)
    cv2.ellipse(img, (320, 350), (45, 60), 0, 0, 360, (0, 140, 255), -1)
    cv2.ellipse(img, (320, 355), (30, 40), 0, 0, 360, (0, 230, 255), -1)
    cv2.circle(img, (320, 360), 18, (255, 255, 255), -1)

    out_path = os.path.join(SAMPLES_DIR, "sample_fire.jpg")
    cv2.imwrite(out_path, img)
    print(f"[+] Saved {out_path}")
    return out_path


def generate_surveillance_video():
    """Generates a 5-second 30fps MP4 video demonstrating moving pedestrians and traffic."""
    out_path = os.path.join(SAMPLES_DIR, "sample_surveillance.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    duration_sec = 5
    total_frames = fps * duration_sec
    w, h = 640, 480

    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    for frame_idx in range(total_frames):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        # Background
        for y in range(h):
            val = int(30 + (y / h) * 30)
            frame[y, :] = (val, val + 5, val + 15)

        # Draw road
        cv2.rectangle(frame, (0, 320), (640, 480), (50, 55, 60), -1)
        cv2.line(frame, (0, 400), (640, 400), (0, 215, 255), 2)

        # Moving car across road
        car_x = int((frame_idx * 6) % 720) - 80
        cv2.rectangle(frame, (car_x, 340), (car_x + 90, 390), (40, 120, 220), -1)
        cv2.circle(frame, (car_x + 20, 392), 9, (20, 20, 20), -1)
        cv2.circle(frame, (car_x + 70, 392), 9, (20, 20, 20), -1)

        # Pedestrians walking on sidewalk
        for i in range(16):
            base_x = 40 + i * 36
            # Walking oscillation
            px = int(base_x + np.sin(frame_idx * 0.15 + i) * 15)
            py = int(220 + (i % 3) * 35)
            # Head
            cv2.circle(frame, (px, py - 26), 6, (200, 180, 160), -1)
            # Body
            cv2.rectangle(frame, (px - 7, py - 20), (px + 7, py), (160, 120, 90), -1)
            # Walking leg phase
            leg_offset = int(np.sin(frame_idx * 0.3 + i) * 6)
            cv2.line(frame, (px - 4, py), (px - 4 + leg_offset, py + 18), (50, 50, 70), 2)
            cv2.line(frame, (px + 4, py), (px + 4 - leg_offset, py + 18), (50, 50, 70), 2)

        # Video timestamp watermark
        cv2.putText(frame, f"CAM-01 [SIMULATED LIVE] | FRAME: {frame_idx:04d}",
                    (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 217, 255), 1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()
    print(f"[+] Saved {out_path}")
    return out_path


def generate_face_image():
    """Generates a sample face portrait image for privacy blurring demonstration."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (35, 40, 48)

    # Uniform & neck
    cv2.ellipse(img, (320, 520), (220, 140), 0, 0, 360, (60, 50, 40), -1)
    cv2.rectangle(img, (290, 320), (350, 400), (180, 200, 225), -1)

    # Head and face
    cv2.ellipse(img, (320, 240), (100, 130), 0, 0, 360, (190, 210, 235), -1)
    cv2.ellipse(img, (320, 160), (105, 70), 0, 180, 360, (40, 30, 25), -1)

    # Eyes & Eyebrows
    cv2.circle(img, (280, 220), 12, (255, 255, 255), -1)
    cv2.circle(img, (360, 220), 12, (255, 255, 255), -1)
    cv2.circle(img, (280, 220), 6, (30, 30, 30), -1)
    cv2.circle(img, (360, 220), 6, (30, 30, 30), -1)
    cv2.line(img, (260, 200), (300, 205), (40, 30, 25), 4)
    cv2.line(img, (340, 205), (380, 200), (40, 30, 25), 4)

    # Nose & Mouth
    cv2.line(img, (320, 220), (315, 260), (140, 160, 190), 3)
    cv2.line(img, (315, 260), (330, 260), (140, 160, 190), 3)
    cv2.ellipse(img, (320, 295), (35, 15), 0, 0, 180, (90, 80, 180), -1)

    out_path = os.path.join(SAMPLES_DIR, "sample_face.jpg")
    cv2.imwrite(out_path, img)
    print(f"[+] Saved {out_path}")
    return out_path


if __name__ == "__main__":
    generate_crowd_image()
    generate_traffic_image()
    generate_fire_image()
    generate_face_image()
    generate_surveillance_video()
    print("[+] All sample media assets generated successfully!")

