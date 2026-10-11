"""
Automated Test Suite for WalkBacker (Touch Grass Open-Source AI)
Validates offline navigation math, solar equations, CoT reasoning, and API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.navigation.breadcrumb import (
    haversine_distance,
    calculate_bearing,
    calculate_return_bearing,
    calculate_turnaround_plan,
    estimate_solar_status,
    BreadcrumbTracker
)
from backend.navigation.gpx_exporter import (
    export_breadcrumbs_to_gpx,
    export_breadcrumbs_to_geojson
)
from backend.nature.identifier import nature_identifier
from backend.nature.taxonomy_db import search_species
from backend.agent.cot_reasoner import cot_reasoner
from backend.agent.model_loader import get_system_memory_status

client = TestClient(app)


def test_system_memory_guard():
    """Verify system RAM telemetry reports valid metrics under 8GB budget."""
    mem = get_system_memory_status()
    assert "total_system_ram_mb" in mem
    assert "available_system_ram_mb" in mem
    assert "process_ram_mb" in mem
    assert mem["process_ram_mb"] > 0
    # Process memory should easily be under 500MB
    assert mem["process_ram_mb"] < 1000


def test_haversine_and_bearing():
    """Verify distance and angle mathematics between known GPS coordinates."""
    # NYC to Philadelphia (approx 130 km)
    nyc_lat, nyc_lon = 40.7128, -74.0060
    philly_lat, philly_lon = 39.9526, -75.1652

    dist = haversine_distance(nyc_lat, nyc_lon, philly_lat, philly_lon)
    assert 120000 < dist < 140000  # meters

    forward_bearing = calculate_bearing(nyc_lat, nyc_lon, philly_lat, philly_lon)
    assert 220 < forward_bearing < 250  # Heading South-West

    return_bearing = calculate_return_bearing(philly_lat, philly_lon, nyc_lat, nyc_lon)
    assert 40 < return_bearing < 70  # Return heading North-East


def test_turnaround_plan():
    """Verify turnaround time and radial distance constraints."""
    plan = calculate_turnaround_plan(total_minutes=60, walking_speed_kmh=4.5, safety_factor=0.85)
    assert plan["total_minutes"] == 60
    assert plan["outbound_minutes"] == 25.5
    assert plan["safety_buffer_minutes"] == 9.0
    assert plan["max_outbound_radius_km"] > 1.5
    assert plan["estimated_steps"] > 5000


def test_solar_estimation():
    """Verify offline solar position calculator."""
    solar = estimate_solar_status(40.7128, -74.0060)
    assert "solar_elevation_deg" in solar
    assert "approx_sunset" in solar
    assert "approx_golden_hour_start" in solar


def test_breadcrumb_tracker():
    """Verify breadcrumb trail recording and return bearing updates."""
    tracker = BreadcrumbTracker(40.7128, -74.0060, "Trailhead")
    assert len(tracker.breadcrumbs) == 1

    # Take step 500m North
    pt_status = tracker.add_point(40.7173, -74.0060)
    assert tracker.total_distance_m > 400
    assert pt_status["walkback_bearing_deg"] > 170  # Should be facing South to return

    wb = tracker.get_walkback_status(40.7173, -74.0060)
    assert wb["cardinal_direction"] == "S"
    assert wb["distance_to_origin_m"] > 400


def test_nature_identification():
    """Verify offline nature identifier matches species by leaf shape and traits."""
    result = nature_identifier.identify_from_text("Found a maple leaf with 5 lobes and brilliant flame orange foliage")
    assert result["identified"] is True
    assert "Maple" in result["species"]["common_name"]
    assert "touch_grass_action" in result

    # Test bird trait query
    bird_res = nature_identifier.identify_from_text("Small bird with black bib and cap calling chick-a-dee")
    assert bird_res["identified"] is True
    assert "Chickadee" in bird_res["species"]["common_name"]


def test_cot_reasoner():
    """Verify full 4-stage Chain of Thought outdoor reasoning decomposition."""
    exp = cot_reasoner.plan_expedition(
        duration_minutes=45,
        vibe="autumn_foliage",
        lat=42.3601,
        lon=-71.0589,
        location_name="Boston Common",
        use_neural=False
    )
    assert exp["success"] is True
    cot = exp["chain_of_thought"]
    assert "step1_environmental_analysis" in cot
    assert "step2_sensory_missions" in cot
    assert "step3_navigation_math" in cot
    assert "step4_screen_minimization" in cot

    # Verify Field Card
    fc = exp["field_card"]
    assert "title" in fc
    assert "turnaround_time" in fc
    assert len(fc["missions"]) >= 3
    assert "audio_script" in exp


def test_gpx_and_geojson_export():
    """Verify GPX and GeoJSON generation."""
    crumbs = [
        {"lat": 40.7128, "lon": -74.0060, "timestamp": "2026-10-11T12:00:00Z", "elevation": 10},
        {"lat": 40.7140, "lon": -74.0050, "timestamp": "2026-10-11T12:05:00Z", "elevation": 12}
    ]
    gpx = export_breadcrumbs_to_gpx(crumbs, "Test Walk")
    assert "<gpx" in gpx
    assert "<trkpt" in gpx

    geojson = export_breadcrumbs_to_geojson(crumbs, "Test Walk")
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 2


def test_api_endpoints():
    """Verify FastAPI routes."""
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_plan = client.post("/api/plan-expedition", json={
        "duration_minutes": 30,
        "vibe": "mindful_birding",
        "lat": 37.7749,
        "lon": -122.4194,
        "location_name": "Golden Gate Park"
    })
    assert res_plan.status_code == 200
    plan_data = res_plan.json()
    assert "chain_of_thought" in plan_data
    assert "field_card" in plan_data

    res_species = client.get("/api/species")
    assert res_species.status_code == 200
    assert res_species.json()["total"] >= 10
