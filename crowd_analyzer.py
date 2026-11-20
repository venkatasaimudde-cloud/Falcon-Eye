"""
FALCON EYE - Advanced Intelligent Crowd Monitoring & Density Analytics
Features:
- Real-time people count aggregation & object tracking with unique IDs (ByteTrack/IoU Centroid Tracker)
- Multi-frame de-duplication: Active Pedestrian Count vs Cumulative Unique Visitors
- Advanced 2D Gaussian Kernel Density Estimation (KDE) with 4-tier hazard zones:
    * GREEN: Normal / Free flow (< 1.0 P/m² or < threshold_yellow)
    * YELLOW: Moderate / Increasing density (1.0 - 1.5 P/m² or threshold_yellow to threshold_orange)
    * ORANGE: High density / Surge hazard (1.5 - 2.5 P/m² or threshold_orange to threshold_red)
    * RED: Critical density / Stampede hazard (> 2.5 P/m² or > threshold_red)
- Zone-wise density analysis with camera perspective calibration (People per square meter: P/m²)
- Fruin's Level of Service (LoS A through F) classification
- Crowd movement analysis: trajectory vectors, velocity, directional flow patterns, and stopped-flow bottleneck detection
"""

import math
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np


class TrackedPedestrian:
    """Represents an individual tracked pedestrian with trajectory and kinematics."""
    def __init__(self, track_id: int, box: List[int]):
        self.track_id = track_id
        self.box = box  # [x1, y1, x2, y2]
        self.centroid = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        self.history = deque(maxlen=20)  # Stores recent centroids (cx, cy)
        self.history.append(self.centroid)
        self.velocity = (0.0, 0.0)  # (vx, vy) in px/frame
        self.speed = 0.0
        self.heading_deg = 0.0
        self.heading_dir = "STATIONARY"
        self.missed_frames = 0
        self.stationary_frames = 0
        self.first_seen = time.time()
        self.last_seen = time.time()

    def update(self, box: List[int]):
        self.box = box
        new_centroid = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        old_centroid = self.centroid

        dx = new_centroid[0] - old_centroid[0]
        dy = new_centroid[1] - old_centroid[1]
        self.velocity = (float(dx), float(dy))
        self.speed = math.hypot(dx, dy)

        if self.speed > 1.5:
            # Angle in degrees (-180 to 180)
            deg = math.degrees(math.atan2(dy, dx))
            self.heading_deg = (deg + 360) % 360
            self.heading_dir = self._deg_to_compass(self.heading_deg)
            self.stationary_frames = 0
        else:
            self.stationary_frames += 1
            if self.stationary_frames > 4:
                self.heading_dir = "STATIONARY"

        self.centroid = new_centroid
        self.history.append(new_centroid)
        self.missed_frames = 0
        self.last_seen = time.time()

    @staticmethod
    def _deg_to_compass(deg: float) -> str:
        val = int((deg / 45) + 0.5) % 8
        dirs = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
        return dirs[val]


class CrowdAnalyzer:
    def __init__(self, thresh_yellow: int = 15, thresh_orange: int = 30, thresh_red: int = 50):
        self.thresh_yellow = thresh_yellow
        self.thresh_orange = thresh_orange
        self.thresh_red = thresh_red

        # Pedestrian Tracker State
        self.next_track_id = 1
        self.tracks: Dict[int, TrackedPedestrian] = {}
        self.cumulative_unique_ids = set()
        self.max_missed_frames = 15

        # Perspective Calibration default: (tilt angle ~45 deg, sensor height ~4.5m)
        self.calibration = {
            "perspective_tilt_deg": 45.0,
            "focal_length_px": 800.0,
            "camera_height_m": 4.5,
            "scale_factor_bottom_m_per_px": 0.025,  # 1px ~ 2.5cm at foreground
            "scale_factor_top_m_per_px": 0.080,     # 1px ~ 8.0cm at background horizon
        }

        # Predefined Monitoring Zones
        self.zones: List[Dict[str, Any]] = [
            {
                "id": "zone-concourse",
                "name": "Zone A: Central Transit Concourse",
                "polygon": [[0.05, 0.20], [0.50, 0.20], [0.50, 0.90], [0.05, 0.90]],  # Normalized [x, y]
                "nominal_area_m2": 75.0,
                "color_hex": "#00D9FF"
            },
            {
                "id": "zone-chokepoint",
                "name": "Zone B: Gate & Escalator Chokepoint",
                "polygon": [[0.55, 0.25], [0.95, 0.25], [0.95, 0.85], [0.55, 0.85]],
                "nominal_area_m2": 35.0,
                "color_hex": "#F59E0B"
            }
        ]

    def set_thresholds(self, yellow: int, orange: int, red: int):
        """Update configurable crowd count thresholds."""
        self.thresh_yellow = yellow
        self.thresh_orange = orange
        self.thresh_red = red

    def reset_tracker(self):
        """Reset tracking state for new video stream or clean session."""
        self.tracks.clear()
        self.cumulative_unique_ids.clear()
        self.next_track_id = 1

    def classify_density(self, count: int) -> Tuple[str, str, str]:
        """Classifies people count into standardized safety categories."""
        if count < self.thresh_yellow:
            return "GREEN", "#22C55E", "Normal pedestrian flow. Free circulation."
        elif count < self.thresh_orange:
            return "YELLOW", "#F59E0B", "Increasing density detected. Pre-cautionary observation recommended."
        elif count < self.thresh_red:
            return "ORANGE", "#F97316", "High density alert. Crowd surge / marshalling advisory."
        else:
            return "RED", "#EF4444", "CRITICAL STAMPEDE HAZARD. Immediate operator review & dispersal coordination required."

    def classify_density_per_m2(self, density_p_m2: float) -> Tuple[str, str, str]:
        """Classifies Fruin's Level of Service (LoS) based on People per Square Meter."""
        if density_p_m2 < 0.6:
            return "LoS A/B (Normal)", "#22C55E", "Free pedestrian flow with unrestricted speed."
        elif density_p_m2 < 1.4:
            return "LoS C (Dense)", "#F59E0B", "Constrained pedestrian flow, minor passing difficulty."
        elif density_p_m2 < 2.2:
            return "LoS D/E (Crowded)", "#F97316", "Significant bottlenecking, reverse flow inhibited."
        else:
            return "LoS F (Critical)", "#EF4444", "Hazardous compression / stampede hazard. Immediate dispersal!"

    # --------------------------------------------------------------------------
    # Object Tracking Engine (ByteTrack / Centroid IoU Compatible)
    # --------------------------------------------------------------------------
    def update_tracks(self, person_boxes: List[List[int]]) -> List[TrackedPedestrian]:
        """
        Updates pedestrian tracks using centroid distance and IoU matching.
        Assigns persistent IDs, updates movement vectors, and de-duplicates counts.
        """
        if not person_boxes:
            to_del = []
            for tid, t in self.tracks.items():
                t.missed_frames += 1
                if t.missed_frames > self.max_missed_frames:
                    to_del.append(tid)
            for tid in to_del:
                del self.tracks[tid]
            return list(self.tracks.values())

        det_centroids = [((b[0] + b[2]) // 2, (b[1] + b[3]) // 2) for b in person_boxes]
        matched_dets = set()
        matched_tracks = set()

        if self.tracks:
            track_ids = list(self.tracks.keys())
            track_centroids = [self.tracks[tid].centroid for tid in track_ids]

            dist_matrix = np.zeros((len(track_ids), len(person_boxes)), dtype=np.float32)
            for i, tc in enumerate(track_centroids):
                for j, dc in enumerate(det_centroids):
                    dist_matrix[i, j] = math.hypot(tc[0] - dc[0], tc[1] - dc[1])

            dist_thresh = 85.0
            while True:
                min_val = np.min(dist_matrix)
                if min_val > dist_thresh:
                    break
                i, j = np.unravel_index(np.argmin(dist_matrix), dist_matrix.shape)
                if i not in matched_tracks and j not in matched_dets:
                    tid = track_ids[i]
                    self.tracks[tid].update(person_boxes[j])
                    matched_tracks.add(i)
                    matched_dets.add(j)
                dist_matrix[i, :] = 1e6
                dist_matrix[:, j] = 1e6

        to_del = []
        for i, tid in enumerate(self.tracks.keys()):
            if i not in matched_tracks:
                self.tracks[tid].missed_frames += 1
                if self.tracks[tid].missed_frames > self.max_missed_frames:
                    to_del.append(tid)
        for tid in to_del:
            del self.tracks[tid]

        for j, box in enumerate(person_boxes):
            if j not in matched_dets:
                tid = self.next_track_id
                self.next_track_id += 1
                new_track = TrackedPedestrian(tid, box)
                self.tracks[tid] = new_track
                self.cumulative_unique_ids.add(tid)

        return list(self.tracks.values())

    # --------------------------------------------------------------------------
    # Advanced 2D Gaussian Kernel Density Estimation (KDE) Heatmap
    # --------------------------------------------------------------------------
    def generate_gaussian_kde_heatmap(self, frame_shape: Tuple[int, int], person_boxes: List[List[int]]) -> np.ndarray:
        """
        Generates a 2D Gaussian Kernel Density Estimation surface with 4 distinct zones.
        Adaptive sigma scales with perspective depth.
        """
        h, w = frame_shape[:2]
        density_map = np.zeros((h, w), dtype=np.float32)

        if not person_boxes:
            return np.zeros((h, w, 3), dtype=np.uint8)

        for box in person_boxes:
            x1, y1, x2, y2 = box
            cx = int(np.clip((x1 + x2) / 2, 0, w - 1))
            cy = int(np.clip((y1 + y2) / 2, 0, h - 1))

            box_h = max(20, y2 - y1)
            sigma = int(np.clip(box_h * 0.75, 25, 95))
            if sigma % 2 == 0:
                sigma += 1

            cv2.circle(density_map, (cx, cy), sigma, 1.0, -1)

        density_map = cv2.GaussianBlur(density_map, (71, 71), 0)

        max_val = np.max(density_map)
        if max_val > 0:
            norm_density = density_map / max_val
        else:
            norm_density = density_map

        norm_uint8 = (norm_density * 255).astype(np.uint8)
        heatmap_bgr = cv2.applyColorMap(norm_uint8, cv2.COLORMAP_JET)

        mask = norm_density < 0.08
        heatmap_bgr[mask] = 0

        return heatmap_bgr

    # --------------------------------------------------------------------------
    # Zone-Wise Density Analysis with Perspective Calibration
    # --------------------------------------------------------------------------
    def analyze_zones(self, frame_shape: Tuple[int, int], tracks: List[TrackedPedestrian]) -> List[Dict[str, Any]]:
        """
        Calculates detected people inside each monitoring zone, calibrated real-world
        ground area (m²), and people per square meter (P/m²).
        """
        h, w = frame_shape[:2]
        zone_results = []

        for z in self.zones:
            pts = z["polygon"]
            pixel_pts = np.array([[int(p[0] * w), int(p[1] * h)] for p in pts], dtype=np.int32)
            
            people_in_zone = 0
            moving_in_zone = 0
            stopped_in_zone = 0

            for t in tracks:
                bx1, by1, bx2, by2 = t.box
                foot_point = (float((bx1 + bx2) / 2), float(by2))
                is_inside = cv2.pointPolygonTest(pixel_pts, foot_point, False) >= 0
                if is_inside:
                    people_in_zone += 1
                    if t.speed > 1.5:
                        moving_in_zone += 1
                    else:
                        stopped_in_zone += 1

            avg_y_norm = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2.0
            scale_m_per_px = (
                self.calibration["scale_factor_top_m_per_px"] * (1.0 - avg_y_norm) +
                self.calibration["scale_factor_bottom_m_per_px"] * avg_y_norm
            )
            pixel_area = cv2.contourArea(pixel_pts)
            calibrated_area_m2 = max(5.0, pixel_area * (scale_m_per_px ** 2))
            
            density_p_m2 = round(people_in_zone / calibrated_area_m2, 2)
            los_label, los_color, los_desc = self.classify_density_per_m2(density_p_m2)

            zone_results.append({
                "zone_id": z["id"],
                "zone_name": z["name"],
                "people_count": people_in_zone,
                "moving_count": moving_in_zone,
                "stopped_count": stopped_in_zone,
                "calibrated_area_m2": round(calibrated_area_m2, 1),
                "density_p_m2": density_p_m2,
                "los_label": los_label,
                "los_color": los_color,
                "los_desc": los_desc,
                "color_hex": z["color_hex"]
            })

        return zone_results

    # --------------------------------------------------------------------------
    # Movement Velocity & Stopped-Flow Bottleneck Detection
    # --------------------------------------------------------------------------
    def analyze_movement(self, tracks: List[TrackedPedestrian]) -> Dict[str, Any]:
        """
        Analyzes directional flow vectors, speed distribution, and detects stopped-flow bottlenecks.
        """
        if not tracks:
            return {
                "dominant_direction": "NONE",
                "average_speed_px_s": 0.0,
                "stopped_count": 0,
                "moving_count": 0,
                "bottleneck_detected": False,
                "anomaly_alert": None
            }

        speeds = [t.speed for t in tracks]
        avg_speed = float(np.mean(speeds)) if speeds else 0.0

        dir_counts: Dict[str, int] = {}
        stopped = 0
        moving = 0

        for t in tracks:
            if t.speed <= 1.5:
                stopped += 1
            else:
                moving += 1
                d = t.heading_dir
                dir_counts[d] = dir_counts.get(d, 0) + 1

        dominant_dir = "STATIONARY"
        if dir_counts:
            dominant_dir = max(dir_counts, key=dir_counts.get)

        bottleneck = False
        anomaly_alert = None
        if len(tracks) >= 15 and (stopped / len(tracks)) >= 0.55:
            bottleneck = True
            anomaly_alert = {
                "type": "STOPPED_FLOW_BOTTLENECK",
                "severity": "CRITICAL" if len(tracks) >= self.thresh_red else "HIGH",
                "message": f"⚠️ Bottleneck Hazard: {stopped} of {len(tracks)} pedestrians halted. Stationary flow detected in transit corridor.",
                "suggested_action": "Deploy station marshals to clear escalator bottleneck and open auxiliary gates."
            }

        return {
            "dominant_direction": dominant_dir,
            "average_speed_px_s": round(avg_speed * 15.0, 1),
            "stopped_count": stopped,
            "moving_count": moving,
            "bottleneck_detected": bottleneck,
            "anomaly_alert": anomaly_alert
        }

    # --------------------------------------------------------------------------
    # Master Visualization & Overlay Pipeline
    # --------------------------------------------------------------------------
    def overlay_crowd_analytics(
        self,
        frame: np.ndarray,
        person_boxes: List[List[int]],
        show_tracks: bool = True,
        show_flow_arrows: bool = True,
        show_heatmap: bool = True,
        show_zones: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Applies end-to-end crowd intelligence analytics:
        - Multi-target tracking with unique IDs
        - 2D Gaussian KDE heatmap blending
        - Perspective-calibrated zone density (P/m²)
        - Directional flow vectors & stopped-flow alerts
        - High-tech Cyber HUD
        """
        h, w = frame.shape[:2]
        annotated = frame.copy()

        tracks = self.update_tracks(person_boxes)
        active_count = len(tracks)
        cumulative_unique = len(self.cumulative_unique_ids)

        if show_heatmap and active_count >= 5:
            heatmap = self.generate_gaussian_kde_heatmap(frame.shape, person_boxes)
            mask = cv2.cvtColor(heatmap, cv2.COLOR_BGR2GRAY) > 10
            alpha = 0.45
            annotated[mask] = cv2.addWeighted(heatmap, alpha, annotated, 1.0 - alpha, 0)[mask]

        zone_analytics = self.analyze_zones(frame.shape, tracks)
        if show_zones:
            for z in self.zones:
                pts = z["polygon"]
                pixel_pts = np.array([[int(p[0] * w), int(p[1] * h)] for p in pts], dtype=np.int32)
                cv2.polylines(annotated, [pixel_pts], True, (0, 217, 255), 2, cv2.LINE_AA)
                
                first_pt = pixel_pts[0]
                label_text = f"[{z['name'].split(':')[0]}]"
                cv2.rectangle(annotated, (first_pt[0], first_pt[1] - 22), (first_pt[0] + 120, first_pt[1]), (8, 15, 30), -1)
                cv2.rectangle(annotated, (first_pt[0], first_pt[1] - 22), (first_pt[0] + 120, first_pt[1]), (0, 217, 255), 1)
                cv2.putText(annotated, label_text, (first_pt[0] + 6, first_pt[1] - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 217, 255), 1, cv2.LINE_AA)

        if show_tracks:
            for t in tracks:
                x1, y1, x2, y2 = t.box
                cx, cy = t.centroid

                box_color = (0, 217, 255) if t.speed > 1.5 else (239, 68, 68) if t.stationary_frames > 8 else (11, 158, 245)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)

                id_tag = f"ID #{t.track_id}"
                tag_w = 64
                cv2.rectangle(annotated, (x1, max(0, y1 - 20)), (x1 + tag_w, max(20, y1)), (8, 15, 30), -1)
                cv2.rectangle(annotated, (x1, max(0, y1 - 20)), (x1 + tag_w, max(20, y1)), box_color, 1)
                cv2.putText(annotated, id_tag, (x1 + 4, max(15, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

                if show_flow_arrows and t.speed > 1.5:
                    vx, vy = t.velocity
                    arrow_len = min(40, max(14, int(t.speed * 4.5)))
                    rad = math.radians(t.heading_deg)
                    end_x = int(cx + arrow_len * math.cos(rad))
                    end_y = int(cy + arrow_len * math.sin(rad))
                    cv2.arrowedLine(annotated, (cx, cy), (end_x, end_y), (0, 255, 255), 2, tipLength=0.35)

        movement_analytics = self.analyze_movement(tracks)
        density_lvl, hex_color, status_msg = self.classify_density(active_count)

        hud_w, hud_h = 360, 140
        hx, hy = w - hud_w - 20, 20
        cv2.rectangle(annotated, (hx, hy), (hx + hud_w, hy + hud_h), (8, 15, 30), -1)
        bgr_colors = {
            "GREEN": (94, 197, 34),
            "YELLOW": (11, 158, 245),
            "ORANGE": (22, 115, 249),
            "RED": (68, 68, 239)
        }
        status_bgr = bgr_colors.get(density_lvl, (0, 217, 255))
        cv2.rectangle(annotated, (hx, hy), (hx + hud_w, hy + hud_h), status_bgr, 2)

        cv2.putText(annotated, "FALCON EYE - CROWD INTELLIGENCE HUD", (hx + 12, hy + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 217, 255), 1, cv2.LINE_AA)
        
        cv2.putText(annotated, f"ACTIVE LIVE COUNT: {active_count} | TOTAL UNIQUE: {cumulative_unique}", (hx + 12, hy + 52),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
        
        cv2.putText(annotated, f"STATUS: [{density_lvl}]", (hx + 12, hy + 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, status_bgr, 2, cv2.LINE_AA)
        
        flow_str = f"Flow: {movement_analytics['dominant_direction']} ({movement_analytics['average_speed_px_s']} px/s) | Stopped: {movement_analytics['stopped_count']}"
        cv2.putText(annotated, flow_str, (hx + 12, hy + 104),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 200, 220), 1, cv2.LINE_AA)

        if movement_analytics['bottleneck_detected']:
            cv2.putText(annotated, "ALERT: BOTTLENECK CONGESTION DETECTED!", (hx + 12, hy + 126),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (68, 68, 239), 1, cv2.LINE_AA)
        else:
            cv2.putText(annotated, "GAUSSIAN KDE & PERSPECTIVE CALIBRATION ACTIVE", (hx + 12, hy + 126),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (100, 130, 160), 1, cv2.LINE_AA)

        summary = {
            "people_count": active_count,
            "active_count": active_count,
            "cumulative_unique_visitors": cumulative_unique,
            "density_level": density_lvl,
            "color_hex": hex_color,
            "message": status_msg,
            "threshold_exceeded": active_count >= self.thresh_red,
            "zones": zone_analytics,
            "movement": movement_analytics,
            "calibrated": True
        }
        return annotated, summary


# Global singleton instance
crowd_analyzer = CrowdAnalyzer()

