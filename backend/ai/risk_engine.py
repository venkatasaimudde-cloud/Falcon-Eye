"""
FALCON EYE - Explainable Situational Risk Assessment Engine
Evaluates situational safety risk using transparent, deterministic rules based strictly on:
- Environmental factors
- Crowd density metrics
- Confirmed hazard events
- Time of day and zone vulnerability
NEVER profiles or evaluates individual persons. Focuses 100% on situational safety.
"""

from typing import Dict, Any, List
from datetime import datetime


class RiskEngine:
    def evaluate_situational_risk(
        self,
        crowd_count: int,
        active_incidents_in_zone: int,
        has_fire_smoke: bool = False,
        has_traffic_collision: bool = False,
        zone_type: str = "Transit Hub",
        hour_of_day: int = None
    ) -> Dict[str, Any]:
        """
        Calculates explainable Safety Risk Index (0-100) and outlines contributing factors.
        """
        if hour_of_day is None:
            hour_of_day = datetime.now().hour

        base_score = 15.0  # Baseline ambient city safety score
        factors: List[str] = []

        # 1. Fire / Smoke hazard impact (immediate critical weight)
        if has_fire_smoke:
            base_score += 45.0
            factors.append("Active combustion/thermal smoke signature confirmed (+45)")

        # 2. Traffic collision impact
        if has_traffic_collision:
            base_score += 30.0
            factors.append("Vehicle collision / roadway obstruction reported (+30)")

        # 3. Crowd density impact
        if crowd_count > 60:
            base_score += 35.0
            factors.append(f"Critical crowd density ({crowd_count} people detected, stampede risk elevation) (+35)")
        elif crowd_count > 30:
            base_score += 20.0
            factors.append(f"High pedestrian volume ({crowd_count} people detected) (+20)")
        elif crowd_count > 15:
            base_score += 8.0
            factors.append(f"Moderate pedestrian movement ({crowd_count} people) (+8)")

        # 4. Compounding incident factor
        if active_incidents_in_zone >= 2:
            base_score += 15.0
            factors.append(f"Multiple co-located active incidents ({active_incidents_in_zone} simultaneous alerts) (+15)")
        elif active_incidents_in_zone == 1:
            base_score += 5.0
            factors.append("Isolated unresolved incident present in perimeter (+5)")

        # 5. Temporal / Environmental context
        is_night = (hour_of_day >= 22 or hour_of_day < 5)
        if is_night:
            base_score += 10.0
            factors.append("Low ambient visibility conditions (Night surveillance operational) (+10)")

        # Cap score between 0 and 100
        risk_score = round(min(100.0, max(0.0, base_score)), 1)

        # Categorize
        if risk_score >= 75.0:
            risk_category = "CRITICAL"
            color_hex = "#EF4444"
            operator_guidance = "Activate priority emergency protocol. Dispatch response teams immediately."
        elif risk_score >= 50.0:
            risk_category = "HIGH"
            color_hex = "#F97316"
            operator_guidance = "Operator review required within 120 seconds. Elevate UAV patrol frequency."
        elif risk_score >= 25.0:
            risk_category = "MODERATE"
            color_hex = "#F59E0B"
            operator_guidance = "Maintain active monitoring. Verify crowd flow indicators."
        else:
            risk_category = "LOW"
            color_hex = "#22C55E"
            operator_guidance = "Normal conditions. Routine AI telemetry scan."

        return {
            "risk_score": risk_score,
            "risk_category": risk_category,
            "color_hex": color_hex,
            "contributing_factors": factors,
            "operator_guidance": operator_guidance,
            "evaluated_at": datetime.utcnow().isoformat() + "Z"
        }


# Global singleton instance
risk_engine = RiskEngine()
