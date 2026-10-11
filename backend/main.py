"""
WalkBacker FastAPI Server
Offline-first backend serving the Touch Grass AI agent and minimal trail UI.
"""
from datetime import datetime
import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import STATIC_DIR, HOST, PORT
from .agent.cot_reasoner import cot_reasoner
from .agent.model_loader import local_engine, get_system_memory_status
from .nature.identifier import nature_identifier
from .nature.taxonomy_db import get_all_species, search_species
from .navigation.breadcrumb import (
    haversine_distance,
    calculate_return_bearing,
    calculate_turnaround_plan,
    estimate_solar_status,
    BreadcrumbTracker
)
from .navigation.gpx_exporter import (
    export_breadcrumbs_to_gpx,
    export_breadcrumbs_to_geojson
)

app = FastAPI(
    title="WalkBacker - Touch Grass Open-Source AI",
    description="Offline-first screen-minimal AI expedition agent & trail navigator",
    version="1.0.0"
)

# Enable CORS for local testing and mobile network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory active session tracker
active_tracker: Optional[BreadcrumbTracker] = None


# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class ExpeditionRequest(BaseModel):
    duration_minutes: int = Field(default=45, ge=10, le=240)
    vibe: str = Field(default="autumn_foliage")
    lat: float = Field(default=40.7128)
    lon: float = Field(default=-74.0060)
    location_name: str = Field(default="Trailhead Park")
    use_neural: bool = Field(default=False)


class NatureIdentifyRequest(BaseModel):
    text_query: Optional[str] = None
    leaf_shape: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    bark_texture: Optional[str] = None
    habitat: Optional[str] = None


class BreadcrumbInitRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    name: str = "Trailhead"


class BreadcrumbPointRequest(BaseModel):
    lat: float
    lon: float
    elevation: Optional[float] = None


class ExportRequest(BaseModel):
    breadcrumbs: List[Dict]
    trail_name: str = "WalkBacker Touch Grass Trail"
    format: str = "gpx"  # "gpx" or "geojson"


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------
@app.get("/api/health")
def health_check():
    """System health check and live 8GB RAM metrics."""
    mem = get_system_memory_status()
    return {
        "status": "healthy",
        "service": "WalkBacker Touch Grass Agent",
        "timestamp": datetime.now().isoformat(),
        "memory": mem,
        "neural_model_loaded": local_engine.is_loaded
    }


@app.get("/api/memory")
def memory_status():
    """Live physical RAM telemetry."""
    return get_system_memory_status()


@app.post("/api/plan-expedition")
def plan_expedition(req: ExpeditionRequest):
    """
    Main Chain-of-Thought (CoT) outdoor planner endpoint.
    Returns 4-stage reasoning trace, pocket field card, and audio narrative.
    """
    global active_tracker
    active_tracker = BreadcrumbTracker(req.lat, req.lon, req.location_name)

    result = cot_reasoner.plan_expedition(
        duration_minutes=req.duration_minutes,
        vibe=req.vibe,
        lat=req.lat,
        lon=req.lon,
        location_name=req.location_name,
        use_neural=req.use_neural
    )
    return result


@app.post("/api/identify-nature")
def identify_nature(req: NatureIdentifyRequest):
    """
    Offline species identification from observational traits or text notes.
    """
    if req.text_query and req.text_query.strip():
        return nature_identifier.identify_from_text(req.text_query)

    results = nature_identifier.identify_by_traits(
        leaf_shape=req.leaf_shape,
        color=req.color,
        category=req.category,
        bark_texture=req.bark_texture,
        habitat=req.habitat
    )
    return {
        "identified": len(results) > 0,
        "candidates": results,
        "count": len(results)
    }


@app.get("/api/species")
def list_species(category: Optional[str] = None):
    """List offline curated taxonomy database."""
    all_s = get_all_species()
    if category:
        all_s = [s for s in all_s if s.get("category") == category]
    return {"species": all_s, "total": len(all_s)}


@app.post("/api/breadcrumbs/init")
def init_breadcrumbs(req: BreadcrumbInitRequest):
    """Initialize a new walking session with origin coordinates."""
    global active_tracker
    active_tracker = BreadcrumbTracker(req.origin_lat, req.origin_lon, req.name)
    return {
        "status": "initialized",
        "origin": active_tracker.origin,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/breadcrumbs/add")
def add_breadcrumb(req: BreadcrumbPointRequest):
    """Record a GPS position and calculate current return-to-base vector."""
    global active_tracker
    if active_tracker is None:
        active_tracker = BreadcrumbTracker(req.lat, req.lon, "Auto Trailhead")

    step_info = active_tracker.add_point(req.lat, req.lon, req.elevation)
    status = active_tracker.get_walkback_status(req.lat, req.lon)
    return {
        **step_info,
        "walkback": status
    }


@app.post("/api/breadcrumbs/export")
def export_trail(req: ExportRequest):
    """Export recorded breadcrumbs as standard GPX XML or GeoJSON."""
    if not req.breadcrumbs:
        raise HTTPException(status_code=400, detail="No breadcrumb coordinates provided")

    if req.format.lower() == "geojson":
        geojson_data = export_breadcrumbs_to_geojson(req.breadcrumbs, req.trail_name)
        return geojson_data

    # Default to GPX format
    gpx_xml = export_breadcrumbs_to_gpx(req.breadcrumbs, req.trail_name)
    return Response(content=gpx_xml, media_type="application/gpx+xml", headers={
        "Content-Disposition": f'attachment; filename="{req.trail_name.replace(" ", "_")}.gpx"'
    })


@app.post("/api/model/load")
def load_model():
    """Explicitly load local open-weight model into CPU memory."""
    success, message = local_engine.load_model()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message, "memory": get_system_memory_status()}


@app.post("/api/model/unload")
def unload_model():
    """Unload model from CPU memory to free RAM."""
    local_engine.unload_model()
    return {"success": True, "message": "Model unloaded", "memory": get_system_memory_status()}


# Mount Static Frontend
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
