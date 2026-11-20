"""
FALCON EYE - Dedicated Fire & Smoke Detection Engine
Combines multi-spectral color space analysis (HSV + YCbCr flame rules),
spatial texture variance, edge degradation (smoke diffusion), and contour analysis.
Provides honest confidence scoring and evidence bounding boxes without relying on standard COCO YOLO.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, List


class FireSmokeDetector:
    def __init__(self):
        # Fire color boundaries in HSV
        # Lower flame (intense yellow/orange/red)
        self.fire_lower1 = np.array([0, 80, 180], dtype=np.uint8)
        self.fire_upper1 = np.array([25, 255, 255], dtype=np.uint8)
        # Upper flame (deep red wrapper)
        self.fire_lower2 = np.array([170, 80, 180], dtype=np.uint8)
        self.fire_upper2 = np.array([180, 255, 255], dtype=np.uint8)

        # Smoke color boundaries in HSV (low saturation, gray/cloudy appearance)
        self.smoke_lower = np.array([0, 0, 75], dtype=np.uint8)
        self.smoke_upper = np.array([180, 45, 215], dtype=np.uint8)

    def analyze_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Processes an image/video frame for fire and smoke signatures.
        Returns:
            - annotated_frame: visual evidence frame with fire/smoke overlays
            - result_dict: detection flags, confidence scores, and bounding boxes
        """
        h, w = frame.shape[:2]
        annotated = frame.copy()
        
        # Color space conversions
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # 1. Fire Detection
        mask_fire1 = cv2.inRange(hsv, self.fire_lower1, self.fire_upper1)
        mask_fire2 = cv2.inRange(hsv, self.fire_lower2, self.fire_upper2)
        mask_fire = cv2.bitwise_or(mask_fire1, mask_fire2)

        # Apply YCbCr fire rules: Y > Cb and Cr > Cb
        y, cr, cb = cv2.split(ycrcb)
        y_cb_rule = (y > cb) & (cr > cb) & (cr > 135)
        mask_fire = cv2.bitwise_and(mask_fire, mask_fire, mask=y_cb_rule.astype(np.uint8) * 255)

        # Morphological filtering to eliminate isolated noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_fire = cv2.morphologyEx(mask_fire, cv2.MORPH_OPEN, kernel)
        mask_fire = cv2.morphologyEx(mask_fire, cv2.MORPH_DILATE, kernel)

        fire_contours, _ = cv2.findContours(mask_fire, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        fire_boxes = []
        fire_area_total = 0
        for cnt in fire_contours:
            area = cv2.contourArea(cnt)
            if area > 120:  # Minimum significant fire region
                x, y_box, bw, bh = cv2.boundingRect(cnt)
                fire_boxes.append([x, y_box, x + bw, y_box + bh])
                fire_area_total += area

        fire_detected = len(fire_boxes) > 0
        fire_confidence = 0.0
        if fire_detected:
            # Scale confidence based on region area and intensity
            area_ratio = min(1.0, fire_area_total / (w * h * 0.08))
            fire_confidence = round(min(0.98, 0.65 + area_ratio * 0.33), 3)

        # 2. Smoke Detection
        mask_smoke = cv2.inRange(hsv, self.smoke_lower, self.smoke_upper)
        # Smoke has low local gradient / edge energy compared to background
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        low_edge_mask = (np.abs(laplacian) < 18).astype(np.uint8) * 255
        mask_smoke = cv2.bitwise_and(mask_smoke, low_edge_mask)
        mask_smoke = cv2.morphologyEx(mask_smoke, cv2.MORPH_OPEN, kernel)

        smoke_contours, _ = cv2.findContours(mask_smoke, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        smoke_boxes = []
        smoke_area_total = 0
        for cnt in smoke_contours:
            area = cv2.contourArea(cnt)
            if area > 350:  # Smoke clouds are typically larger
                x, y_box, bw, bh = cv2.boundingRect(cnt)
                smoke_boxes.append([x, y_box, x + bw, y_box + bh])
                smoke_area_total += area

        smoke_detected = len(smoke_boxes) > 0
        smoke_confidence = 0.0
        if smoke_detected:
            smoke_ratio = min(1.0, smoke_area_total / (w * h * 0.12))
            smoke_confidence = round(min(0.92, 0.55 + smoke_ratio * 0.37), 3)

        # Annotate visual evidence
        if fire_detected:
            for box in fire_boxes:
                x1, y1, x2, y2 = box
                # Red flame box with flashing-style double outline
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(annotated, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), (0, 165, 255), 1)
                
                label = f"FIRE DETECTED ({int(fire_confidence * 100)}%)"
                cv2.rectangle(annotated, (x1, max(0, y1 - 22)), (x1 + 180, max(22, y1)), (0, 0, 200), -1)
                cv2.putText(annotated, label, (x1 + 4, max(16, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        if smoke_detected and not fire_detected:
            for box in smoke_boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (180, 180, 180), 2)
                label = f"SMOKE SIGNATURE ({int(smoke_confidence * 100)}%)"
                cv2.rectangle(annotated, (x1, max(0, y1 - 22)), (x1 + 190, max(22, y1)), (80, 80, 80), -1)
                cv2.putText(annotated, label, (x1 + 4, max(16, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # HUD Overlay if hazards present
        if fire_detected or smoke_detected:
            hud_text = "HAZARD: FIRE DETECTED" if fire_detected else "HAZARD: SMOKE DETECTED"
            hud_color = (0, 0, 255) if fire_detected else (0, 165, 255)
            cv2.rectangle(annotated, (10, h - 50), (320, h - 10), (10, 15, 30), -1)
            cv2.rectangle(annotated, (10, h - 50), (320, h - 10), hud_color, 2)
            cv2.putText(annotated, hud_text, (20, h - 23),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, hud_color, 2, cv2.LINE_AA)

        return annotated, {
            "fire_detected": fire_detected,
            "fire_confidence": fire_confidence,
            "fire_boxes": fire_boxes,
            "smoke_detected": smoke_detected,
            "smoke_confidence": smoke_confidence,
            "smoke_boxes": smoke_boxes,
            "requires_human_verification": fire_detected or smoke_detected
        }


# Global singleton instance
fire_smoke_detector = FireSmokeDetector()
