"""
FALCON EYE - YOLOv8 Computer Vision Object Detection Engine
Performs real-time object detection for public safety:
People, Cars, Buses, Trucks, Motorcycles, Bicycles, Backpacks, etc.
Optimized for high-speed CPU inference with custom bounding box rendering.
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Tuple, Any
from ultralytics import YOLO

# Model path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")


class ObjectDetector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObjectDetector, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return
        # Load YOLOv8 nano model (lightweight, runs effortlessly on standard laptops)
        if os.path.exists(MODEL_PATH):
            self.model = YOLO(MODEL_PATH)
        else:
            self.model = YOLO("yolov8n.pt")
        self.initialized = True

        # Safety-relevant target classes to track
        self.target_classes = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
            24: "backpack",
            26: "handbag",
            28: "suitcase"
        }

        # Color palette for classes (BGR for OpenCV)
        self.class_colors = {
            "person": (255, 217, 0),       # Electric Cyan (BGR: 0, 217, 255 -> 255, 217, 0)
            "car": (255, 120, 40),         # Azure Blue
            "bus": (0, 165, 255),          # Amber / Orange
            "truck": (0, 140, 255),        # Deep Orange
            "motorcycle": (200, 200, 0),   # Cyan Teal
            "bicycle": (150, 255, 150),    # Light Green
            "backpack": (200, 100, 255),   # Magenta Pink
            "default": (255, 200, 50)
        }

    def detect_frame(self, frame: np.ndarray, conf_threshold: float = 0.35) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, int]]:
        """
        Run inference on a single OpenCV BGR frame.
        Returns:
            - annotated_frame: np.ndarray with bounding boxes and HUD styling
            - detections: list of detection dicts
            - counts: dictionary of detected class counts
        """
        # Run inference
        results = self.model(frame, conf=conf_threshold, verbose=False)
        result = results[0]

        detections = []
        counts = {}
        annotated_frame = frame.copy()

        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = xyxy

                cls_name = result.names.get(cls_id, f"obj_{cls_id}")

                # Accumulate counts
                counts[cls_name] = counts.get(cls_name, 0) + 1

                detections.append({
                    "class": cls_name,
                    "confidence": round(conf, 3),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })

                # Visual bounding box rendering
                color = self.class_colors.get(cls_name, self.class_colors["default"])
                
                # Draw rounded-corner look rectangle
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                # Draw corner brackets for futuristic HUD look
                bracket_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
                if bracket_len > 2:
                    # Top-left
                    cv2.line(annotated_frame, (x1, y1), (x1 + bracket_len, y1), (255, 255, 255), 2)
                    cv2.line(annotated_frame, (x1, y1), (x1, y1 + bracket_len), (255, 255, 255), 2)
                    # Bottom-right
                    cv2.line(annotated_frame, (x2, y2), (x2 - bracket_len, y2), (255, 255, 255), 2)
                    cv2.line(annotated_frame, (x2, y2), (x2, y2 - bracket_len), (255, 255, 255), 2)

                # Label tag
                label = f"{cls_name.upper()} {int(conf * 100)}%"
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                
                # Label background
                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 20)), (x1 + w + 6, max(20, y1)), (16, 27, 45), -1)
                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 20)), (x1 + w + 6, max(20, y1)), color, 1)
                cv2.putText(annotated_frame, label, (x1 + 3, max(15, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # Draw HUD status overlay on top-left of frame
        people_count = counts.get("person", 0)
        vehicle_count = sum(counts.get(k, 0) for k in ["car", "bus", "truck", "motorcycle"])
        
        hud_bg = (10, 15, 30)
        cv2.rectangle(annotated_frame, (10, 10), (280, 50), hud_bg, -1)
        cv2.rectangle(annotated_frame, (10, 10), (280, 50), (0, 217, 255), 1)
        hud_text = f"PEOPLE: {people_count} | VEHICLES: {vehicle_count}"
        cv2.putText(annotated_frame, hud_text, (20, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 217, 255), 1, cv2.LINE_AA)

        return annotated_frame, detections, counts

    def process_image_file(self, file_path: str, conf_threshold: float = 0.35) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, int]]:
        """Read image from path and detect objects."""
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not read image from {file_path}")
        return self.detect_frame(img, conf_threshold)


# Global singleton instance
detector = ObjectDetector()
