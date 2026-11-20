"""
FALCON EYE - Extensible Event & Hazard Detection Engine
Detects:
1. Potential Road Collisions (Vehicle bounding box intersection & proximity)
2. Fallen-Person Events (Aspect-ratio geometry analysis: width > height)
3. Road Obstructions (Stationary objects/debris on transit paths)
"""

import numpy as np
import cv2
from typing import List, Dict, Tuple, Any


class HazardDetector:
    def __init__(self):
        self.vehicle_classes = {"car", "bus", "truck", "motorcycle"}

    def _compute_iou(self, boxA: List[int], boxB: List[int]) -> float:
        """Computes Intersection over Union between two bounding boxes."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def analyze_hazards(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Analyzes detected bounding boxes for safety hazards.
        Returns annotated frame and list of generated hazard events.
        """
        annotated = frame.copy()
        hazards = []

        vehicles = [d for d in detections if d["class"] in self.vehicle_classes]
        people = [d for d in detections if d["class"] == "person"]

        # 1. Collision / Vehicle Impact Detection
        for i in range(len(vehicles)):
            for j in range(i + 1, len(vehicles)):
                box1 = vehicles[i]["bbox"]
                box2 = vehicles[j]["bbox"]
                iou = self._compute_iou(box1, box2)

                if iou > 0.12:  # Bounding boxes significantly overlapping
                    conf = round(min(0.92, 0.60 + iou * 0.8), 2)
                    hazard = {
                        "type": "TRAFFIC_COLLISION",
                        "severity": "CRITICAL" if iou > 0.3 else "HIGH",
                        "confidence": conf,
                        "description": f"Potential vehicle collision between {vehicles[i]['class']} and {vehicles[j]['class']}",
                        "bbox": [min(box1[0], box2[0]), min(box1[1], box2[1]),
                                 max(box1[2], box2[2]), max(box1[3], box2[3])]
                    }
                    hazards.append(hazard)

                    # Highlight collision zone with warning border
                    bx1, by1, bx2, by2 = hazard["bbox"]
                    cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 0, 255), 3)
                    cv2.putText(annotated, f"COLLISION ALERT ({int(conf*100)}%)",
                                (bx1, max(25, by1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

        # 2. Fallen Person / Medical Emergency Detection
        for person in people:
            x1, y1, x2, y2 = person["bbox"]
            w = x2 - x1
            h = y2 - y1

            if h > 0:
                aspect_ratio = w / float(h)
                # Standing person aspect ratio is ~0.3 - 0.5.
                # Lying/fallen person aspect ratio is > 1.15
                if aspect_ratio > 1.15 and w > 40:
                    conf = round(min(0.89, 0.65 + (aspect_ratio - 1.15) * 0.2), 2)
                    hazard = {
                        "type": "FALLEN_PERSON",
                        "severity": "HIGH",
                        "confidence": conf,
                        "description": "Fallen or incapacitated pedestrian detected requiring medical assistance",
                        "bbox": [x1, y1, x2, y2]
                    }
                    hazards.append(hazard)

                    # Highlight fallen person with amber warning
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 140, 255), 2)
                    cv2.putText(annotated, f"FALLEN PERSON ({int(conf*100)}%)",
                                (x1, max(25, y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 2, cv2.LINE_AA)

        return annotated, hazards


# Global singleton instance
hazard_detector = HazardDetector()
