"""
FALCON EYE - Geospatial Intelligence & Route Optimization Engine
Features:
- GIS distance computation via Haversine formula
- Nearest Emergency Facility locator (Hospitals, Fire Stations, Police Patrols)
- Realistic Emergency Route path generation with distance (km) and travel time (minutes)
- State-wide Emergency Service POIs in Telangana & Andhra Pradesh
"""

import math
from typing import List, Dict, Any, Tuple


class GeoEngine:
    def __init__(self):
        # Known emergency service landmarks across Telangana & Andhra Pradesh
        self.emergency_facilities = [
            # --- TELANGANA ---
            {
                "id": 1,
                "name": "Osmania General Emergency Hospital",
                "state": "Telangana",
                "city": "Hyderabad",
                "type": "HOSPITAL",
                "lat": 17.3780,
                "lon": 78.4740,
                "contact": "+91 40 2460 0146",
                "ambulances_available": 6
            },
            {
                "id": 2,
                "name": "Gandhi Medical Emergency Trauma Care",
                "state": "Telangana",
                "city": "Secunderabad",
                "type": "HOSPITAL",
                "lat": 17.4250,
                "lon": 78.5020,
                "contact": "+91 40 2750 5566",
                "ambulances_available": 8
            },
            {
                "id": 3,
                "name": "MGM Government Civil Hospital",
                "state": "Telangana",
                "city": "Warangal",
                "type": "HOSPITAL",
                "lat": 17.9784,
                "lon": 79.5941,
                "contact": "+91 870 244 4250",
                "ambulances_available": 5
            },
            {
                "id": 4,
                "name": "Central Fire & Rescue Command Station",
                "state": "Telangana",
                "city": "Hyderabad",
                "type": "FIRE_STATION",
                "lat": 17.3620,
                "lon": 78.4750,
                "contact": "101 / +91 40 2344 2944",
                "fire_tenders_available": 4
            },
            {
                "id": 5,
                "name": "Warangal Division Fire Station",
                "state": "Telangana",
                "city": "Warangal",
                "type": "FIRE_STATION",
                "lat": 17.9689,
                "lon": 79.5941,
                "contact": "101 / +91 870 257 7101",
                "fire_tenders_available": 3
            },
            {
                "id": 6,
                "name": "Hyderabad City Police Commissionerate HQ",
                "state": "Telangana",
                "city": "Hyderabad",
                "type": "POLICE_HQ",
                "lat": 17.4010,
                "lon": 78.4780,
                "contact": "100 / +91 40 2785 2400",
                "patrol_units_available": 12
            },
            {
                "id": 7,
                "name": "Cyberabad Police Commissionerate HQ",
                "state": "Telangana",
                "city": "Gachibowli",
                "type": "POLICE_HQ",
                "lat": 17.4399,
                "lon": 78.3639,
                "contact": "100 / +91 40 2785 3400",
                "patrol_units_available": 10
            },

            # --- ANDHRA PRADESH ---
            {
                "id": 8,
                "name": "King George Hospital (KGH) Trauma Care",
                "state": "Andhra Pradesh",
                "city": "Visakhapatnam",
                "type": "HOSPITAL",
                "lat": 17.7088,
                "lon": 83.3056,
                "contact": "+91 891 256 4891",
                "ambulances_available": 9
            },
            {
                "id": 9,
                "name": "Government General Hospital (Old GGH)",
                "state": "Andhra Pradesh",
                "city": "Vijayawada",
                "type": "HOSPITAL",
                "lat": 16.5165,
                "lon": 80.6322,
                "contact": "+91 866 257 5800",
                "ambulances_available": 7
            },
            {
                "id": 10,
                "name": "SVIMS Super Specialty Hospital",
                "state": "Andhra Pradesh",
                "city": "Tirupati",
                "type": "HOSPITAL",
                "lat": 13.6369,
                "lon": 79.4042,
                "contact": "+91 877 228 7777",
                "ambulances_available": 6
            },
            {
                "id": 11,
                "name": "Visakhapatnam City Police Commissionerate HQ",
                "state": "Andhra Pradesh",
                "city": "Visakhapatnam",
                "type": "POLICE_HQ",
                "lat": 17.7215,
                "lon": 83.3150,
                "contact": "100 / +91 891 256 5454",
                "patrol_units_available": 11
            },
            {
                "id": 12,
                "name": "Vijayawada City Police Commissionerate",
                "state": "Andhra Pradesh",
                "city": "Vijayawada",
                "type": "POLICE_HQ",
                "lat": 16.5062,
                "lon": 80.6480,
                "contact": "100 / +91 866 257 4100",
                "patrol_units_available": 8
            },
            {
                "id": 13,
                "name": "Visakhapatnam Port Fire & Rescue Station",
                "state": "Andhra Pradesh",
                "city": "Visakhapatnam",
                "type": "FIRE_STATION",
                "lat": 17.6967,
                "lon": 83.2980,
                "contact": "101 / +91 891 287 3101",
                "fire_tenders_available": 5
            },
            {
                "id": 14,
                "name": "Kurnool Government General Hospital",
                "state": "Andhra Pradesh",
                "city": "Kurnool",
                "type": "HOSPITAL",
                "lat": 15.8281,
                "lon": 78.0373,
                "contact": "+91 8518 255 101",
                "ambulances_available": 4
            }
        ]

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points on Earth in kilometers.
        """
        R = 6371.0  # Earth radius in kilometers
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon / 2) * math.sin(dLon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return round(distance, 2)

    def find_nearest_facilities(self, target_lat: float, target_lon: float, facility_type: str = None) -> List[Dict[str, Any]]:
        """
        Ranks emergency facilities by proximity to target coordinates.
        """
        results = []
        for fac in self.emergency_facilities:
            if facility_type and fac["type"] != facility_type:
                continue
            dist_km = self.haversine_distance(target_lat, target_lon, fac["lat"], fac["lon"])
            # Estimated emergency siren travel time assuming average 45 km/h urban speed
            eta_minutes = round(max(1.0, (dist_km / 45.0) * 60.0), 1)

            entry = fac.copy()
            entry["distance_km"] = dist_km
            entry["eta_minutes"] = eta_minutes
            results.append(entry)

        # Sort by distance
        results.sort(key=lambda x: x["distance_km"])
        return results

    def compute_emergency_route(self, from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> Dict[str, Any]:
        """
        Computes emergency transit route points, road distance, and travel time.
        Uses realistic multi-segment path along urban/highway grid.
        """
        direct_dist = self.haversine_distance(from_lat, from_lon, to_lat, to_lon)
        # Road distance factor (typically ~1.22x Euclidean)
        road_distance_km = round(direct_dist * 1.22, 2)
        # Average emergency vehicle transit speed with siren: 48 km/h
        travel_time_min = round(max(1.5, (road_distance_km / 48.0) * 60.0), 1)

        # Generate realistic waypoints along the route
        waypoints = [
            {"lat": round(from_lat, 6), "lon": round(from_lon, 6)},
            # Intermediate waypoint 1 (turn onto main arterial avenue)
            {"lat": round(from_lat + (to_lat - from_lat) * 0.45 + 0.0005, 6),
             "lon": round(from_lon + (to_lon - from_lon) * 0.25, 6)},
            # Intermediate waypoint 2 (transit corridor)
            {"lat": round(from_lat + (to_lat - from_lat) * 0.75, 6),
             "lon": round(from_lon + (to_lon - from_lon) * 0.85 + 0.0004, 6)},
            {"lat": round(to_lat, 6), "lon": round(to_lon, 6)}
        ]

        return {
            "origin": {"lat": from_lat, "lon": from_lon},
            "destination": {"lat": to_lat, "lon": to_lon},
            "road_distance_km": road_distance_km,
            "estimated_travel_time_min": travel_time_min,
            "route_waypoints": waypoints,
            "routing_source": "Falcon Urban Road Network Model (Simulated GIS Route)"
        }


# Global singleton instance
geo_engine = GeoEngine()
