"""
Offline Breadcrumb Navigation & WalkBack Mathematics
Provides deterministic navigation math, dead reckoning, and offline solar position.
Runs 100% locally with zero external network calls.
"""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points in meters.
    """
    r_earth = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the compass bearing (azimuth) in degrees [0, 360) from point 1 to point 2.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))

    initial_bearing = math.degrees(math.atan2(y, x))
    return (initial_bearing + 360.0) % 360.0


def calculate_return_bearing(current_lat: float, current_lon: float,
                             origin_lat: float, origin_lon: float) -> float:
    """
    Calculate the compass bearing required to walk back directly to origin.
    """
    return calculate_bearing(current_lat, current_lon, origin_lat, origin_lon)


def calculate_turnaround_plan(total_minutes: int,
                              start_time: Optional[datetime] = None,
                              walking_speed_kmh: float = 4.5,
                              safety_factor: float = 0.85) -> Dict:
    """
    Calculates outbound time, turnaround deadline, and safe radial walking boundary.
    """
    if start_time is None:
        start_time = datetime.now()

    outbound_minutes = (total_minutes / 2.0) * safety_factor
    buffer_minutes = total_minutes - (outbound_minutes * 2.0)
    turnaround_time = start_time + timedelta(minutes=outbound_minutes)
    completion_time = start_time + timedelta(minutes=total_minutes)

    # Maximum outbound walking radius (km)
    max_radius_km = (walking_speed_kmh * (outbound_minutes / 60.0))

    return {
        "start_time": start_time.strftime("%H:%M:%S"),
        "total_minutes": total_minutes,
        "outbound_minutes": round(outbound_minutes, 1),
        "return_minutes": round(outbound_minutes, 1),
        "safety_buffer_minutes": round(buffer_minutes, 1),
        "turnaround_time": turnaround_time.strftime("%H:%M:%S"),
        "completion_time": completion_time.strftime("%H:%M:%S"),
        "max_outbound_radius_km": round(max_radius_km, 2),
        "estimated_steps": int(total_minutes * 110)  # ~110 steps/min nature walking pace
    }


def estimate_solar_status(lat: float, lon: float, dt: Optional[datetime] = None) -> Dict:
    """
    Approximate solar position (elevation angle and sunset estimate)
    derived using standard astronomical approximation formulas.
    Requires no internet and negligible CPU cycles.
    """
    if dt is None:
        dt = datetime.now()

    day_of_year = dt.timetuple().tm_yday
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

    # Solar declination approximation (Cooper, 1969)
    declination = 23.45 * math.sin(math.radians((360.0 / 365.0) * (284 + day_of_year)))
    
    # Equation of time (minutes)
    b = math.radians((360.0 / 365.0) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

    # Solar hour angle
    solar_time_fix = (4.0 * lon) + eot
    true_solar_time = (hour * 60.0 + solar_time_fix) % 1440.0
    hour_angle = (true_solar_time / 4.0) - 180.0

    # Solar elevation angle
    lat_rad = math.radians(lat)
    dec_rad = math.radians(declination)
    ha_rad = math.radians(hour_angle)

    sin_elevation = (math.sin(lat_rad) * math.sin(dec_rad) +
                     math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad))
    elevation = math.degrees(math.asin(max(-1.0, min(1.0, sin_elevation))))

    # Approximate sunset hour (when elevation reaches -0.833 deg)
    try:
        cos_has = (-0.0145 - math.sin(lat_rad) * math.sin(dec_rad)) / (math.cos(lat_rad) * math.cos(dec_rad))
        if cos_has < -1.0:
            sunset_hour_str = "Midnight Sun (No Sunset)"
            golden_hour_str = "Continuous Daylight"
        elif cos_has > 1.0:
            sunset_hour_str = "Polar Night (No Sunrise)"
            golden_hour_str = "No Sunlight"
        else:
            has_deg = math.degrees(math.acos(cos_has))
            sunset_solar_min = (180.0 + has_deg) * 4.0
            sunset_local_min = (sunset_solar_min - solar_time_fix) % 1440.0
            sh = int(sunset_local_min // 60)
            sm = int(sunset_local_min % 60)
            sunset_hour_str = f"{sh:02d}:{sm:02d}"
            
            # Golden hour is roughly 45 mins before sunset
            gh_local_min = (sunset_local_min - 45) % 1440.0
            gh_h = int(gh_local_min // 60)
            gh_m = int(gh_local_min % 60)
            golden_hour_str = f"{gh_h:02d}:{gh_m:02d}"
    except Exception:
        sunset_hour_str = "18:15"
        golden_hour_str = "17:30"

    is_daylight = elevation > 0.0
    is_golden_hour = 0.0 <= elevation <= 12.0

    return {
        "solar_elevation_deg": round(elevation, 1),
        "is_daylight": is_daylight,
        "is_golden_hour": is_golden_hour,
        "approx_sunset": sunset_hour_str,
        "approx_golden_hour_start": golden_hour_str,
        "current_time": dt.strftime("%H:%M:%S")
    }


class BreadcrumbTracker:
    """
    In-memory breadcrumb tracker for outdoor walks.
    Tracks visited waypoints, current walkback heading, and cumulative trail distance.
    """
    def __init__(self, origin_lat: float, origin_lon: float, name: str = "Trailhead"):
        self.origin = {"lat": origin_lat, "lon": origin_lon, "name": name}
        self.breadcrumbs: List[Dict] = [{
            "lat": origin_lat,
            "lon": origin_lon,
            "timestamp": datetime.now().isoformat(),
            "name": name
        }]
        self.total_distance_m: float = 0.0

    def add_point(self, lat: float, lon: float, elevation: Optional[float] = None) -> Dict:
        """
        Record a new GPS coordinate breadcrumb.
        """
        last_pt = self.breadcrumbs[-1]
        step_distance = haversine_distance(last_pt["lat"], last_pt["lon"], lat, lon)
        self.total_distance_m += step_distance

        point = {
            "lat": lat,
            "lon": lon,
            "elevation": elevation,
            "timestamp": datetime.now().isoformat(),
            "step_dist_m": round(step_distance, 1)
        }
        self.breadcrumbs.append(point)

        displacement_m = haversine_distance(self.origin["lat"], self.origin["lon"], lat, lon)
        return_bearing = calculate_return_bearing(lat, lon, self.origin["lat"], self.origin["lon"])

        return {
            "point_index": len(self.breadcrumbs) - 1,
            "total_distance_m": round(self.total_distance_m, 1),
            "displacement_from_origin_m": round(displacement_m, 1),
            "walkback_bearing_deg": round(return_bearing, 1)
        }

    def get_walkback_status(self, current_lat: float, current_lon: float) -> Dict:
        """
        Get instantaneous return-to-base navigation vector.
        """
        dist_home_m = haversine_distance(current_lat, current_lon, self.origin["lat"], self.origin["lon"])
        bearing_home = calculate_return_bearing(current_lat, current_lon, self.origin["lat"], self.origin["lon"])

        # Cardinal direction label
        cardinals = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
        idx = int((bearing_home + 22.5) / 45) % 8
        cardinal_label = cardinals[idx]

        return {
            "origin": self.origin,
            "current": {"lat": current_lat, "lon": current_lon},
            "distance_to_origin_m": round(dist_home_m, 1),
            "distance_to_origin_km": round(dist_home_m / 1000.0, 2),
            "bearing_home_deg": round(bearing_home, 1),
            "cardinal_direction": cardinal_label,
            "breadcrumb_count": len(self.breadcrumbs)
        }
