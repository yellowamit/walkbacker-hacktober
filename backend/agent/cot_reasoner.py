"""
WalkBacker Chain of Thought (CoT) Reasoner
Executes multi-stage outdoor reasoning to produce screen-minimal expeditions.
Preserves full context and rationale at every stage.
"""
from datetime import datetime, timedelta
import math
import time
from typing import Dict, List, Optional

from .prompts import COT_SYSTEM_PROMPT, VIBE_CATALOG
from .model_loader import local_engine, get_system_memory_status
from ..navigation.breadcrumb import (
    calculate_turnaround_plan,
    estimate_solar_status,
    calculate_return_bearing
)
from ..nature.taxonomy_db import SPECIES_CATALOG


class WalkBackerReasoner:
    """
    Outdoor expedition planner implementing Chain-of-Thought (CoT) decomposition.
    """
    def __init__(self):
        self.vibes = VIBE_CATALOG
        self.species = SPECIES_CATALOG

    def plan_expedition(self,
                        duration_minutes: int = 45,
                        vibe: str = "autumn_foliage",
                        lat: float = 40.7128,
                        lon: float = -74.0060,
                        location_name: str = "Trailhead Base",
                        use_neural: bool = False) -> Dict:
        """
        Executes the 4-stage Chain of Thought reasoning pipeline.
        """
        start_ts = time.time()
        now = datetime.now()

        # Retrieve vibe specifications
        vibe_spec = self.vibes.get(vibe, self.vibes["autumn_foliage"])

        # -------------------------------------------------------------
        # STAGE 1: Environmental & Solar Analysis (<thought_environment>)
        # -------------------------------------------------------------
        solar_info = estimate_solar_status(lat, lon, now)
        turnaround_info = calculate_turnaround_plan(duration_minutes, now)

        env_thought = (
            f"Analyzing outdoor conditions at ({lat:.4f}, {lon:.4f}) at local time {solar_info['current_time']}. "
            f"Solar elevation is {solar_info['solar_elevation_deg']} deg. "
            f"Approximate sunset is at {solar_info['approx_sunset']} (golden hour begins ~{solar_info['approx_golden_hour_start']}). "
            f"With {duration_minutes} minutes allocated, safe outbound movement must cease after {turnaround_info['outbound_minutes']} minutes "
            f"at exactly {turnaround_info['turnaround_time']} to preserve a {turnaround_info['safety_buffer_minutes']} min reserve buffer. "
            f"Maximum radial penetration limit is {turnaround_info['max_outbound_radius_km']} km."
        )

        # -------------------------------------------------------------
        # STAGE 2: Sensory Touch-Grass Missions (<thought_sensory>)
        # -------------------------------------------------------------
        # Select matching botanical and wildlife targets for tactile engagement
        selected_species = [s for s in self.species if s.get("category") in ["tree_foliage", "songbird", "fungi"]]
        species_target = selected_species[0] if selected_species else self.species[0]
        secondary_target = selected_species[1] if len(selected_species) > 1 else self.species[-1]

        sensory_missions = [
            {
                "id": "mission_acoustic",
                "sense": "Acoustic Grounding",
                "action": vibe_spec["acoustic_cue"],
                "rationale": "Breaks digital visual fixation by anchoring perception to environmental soundscapes."
            },
            {
                "id": "mission_botanical",
                "sense": "Tactile Flora Exploration",
                "action": f"Identify {species_target['common_name']}. {species_target['touch_grass_cue']}",
                "rationale": f"Direct physical interaction with {species_target['leaf_shape']} and texture."
            },
            {
                "id": "mission_mindful_observation",
                "sense": "Visual Horizon Re-centering",
                "action": f"Look for {vibe_spec['color_target']}. Notice how natural light reflects through the canopy.",
                "rationale": "Re-trains optic focus from phone screen focal lengths (30cm) to infinity distances."
            }
        ]

        sensory_thought = (
            f"Formulating anti-screen grounding objectives for vibe '{vibe_spec['title']}'. "
            f"Rather than passive walking with headphones or screen monitoring, the user is given 3 tactile tasks: "
            f"1) {sensory_missions[0]['action']} "
            f"2) {sensory_missions[1]['action']} "
            f"3) {sensory_missions[2]['action']}. "
            f"These shift awareness outward into the surrounding habitat."
        )

        # -------------------------------------------------------------
        # STAGE 3: Safe Navigation & Turnaround Mathematics (<thought_navigation>)
        # -------------------------------------------------------------
        # Calculate outbound destination coordinate estimation (heading east-northeast 65 deg by default)
        outbound_bearing_deg = 65.0
        return_bearing_deg = (outbound_bearing_deg + 180.0) % 360.0
        
        # Calculate approximate turnaround coordinate offset
        dist_km = turnaround_info["max_outbound_radius_km"]
        d_lat = (dist_km / 111.0) * math.cos(math.radians(outbound_bearing_deg))
        d_lon = (dist_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(math.radians(outbound_bearing_deg))
        turnaround_lat = lat + d_lat
        turnaround_lon = lon + d_lon

        nav_thought = (
            f"Calculating navigational boundaries: Walking speed is calibrated at 4.5 km/h. "
            f"Outbound threshold: {turnaround_info['outbound_minutes']} minutes. "
            f"Outbound destination limit: lat {turnaround_lat:.5f}, lon {turnaround_lon:.5f}. "
            f"When turnaround alarm alerts at {turnaround_info['turnaround_time']}, "
            f"the required reverse heading home is {return_bearing_deg:.1f} degrees (South-West). "
            f"If GPS signal weakens under canopy, dead reckoning maintains safety."
        )

        # -------------------------------------------------------------
        # STAGE 4: Screen Minimization Protocol & Pocket Field Card (<thought_screen_minimization>)
        # -------------------------------------------------------------
        min_thought = (
            f"Synthesizing delivery artifact for screen-free execution. "
            f"User should digest the Field Card in < 30 seconds before sliding phone into pocket. "
            f"A single audio chime will trigger at {turnaround_info['turnaround_time']} (Turnaround point). "
            f"Total recommended on-trail screen glances: exactly 1 (to confirm home compass bearing if needed)."
        )

        # Optional Neural Augmentation if user specifically enabled it and memory permits
        neural_reflection = None
        if use_neural and local_engine.is_loaded:
            prompt = f"Trail Context: {vibe_spec['title']} at {location_name}. Briefly suggest one poetic nature observation for a walker touching grass:"
            neural_reflection = local_engine.generate(prompt, max_new_tokens=45)

        # Build Pocket Field Card
        field_card = {
            "title": f"🌿 {vibe_spec['title']}",
            "location": location_name,
            "expedition_duration_min": duration_minutes,
            "turnaround_time": turnaround_info["turnaround_time"],
            "max_distance_km": turnaround_info["max_outbound_radius_km"],
            "return_bearing_deg": round(return_bearing_deg, 1),
            "cardinal_home": "SW",
            "key_species": {
                "name": species_target["common_name"],
                "scientific": species_target["scientific_name"],
                "cue": species_target["touch_grass_cue"]
            },
            "missions": [m["action"] for m in sensory_missions],
            "neural_note": neural_reflection or "Breathe deeply, feel the cool autumn air, and put your screen away."
        }

        # Build Spoken Audio Narrative (for offline Web Speech synthesis)
        audio_script = (
            f"Welcome to your Touch Grass expedition at {location_name}. "
            f"You have {duration_minutes} minutes total. "
            f"Your outbound walk ends at {turnaround_info['turnaround_time']}, when a chime will sound. "
            f"Today's missions: First, {sensory_missions[0]['action']}. "
            f"Second, {sensory_missions[1]['action']}. "
            f"Now, put your phone in your pocket, look up, and enjoy the trail."
        )

        latency_ms = round((time.time() - start_ts) * 1000, 2)
        mem_status = get_system_memory_status()

        return {
            "success": True,
            "latency_ms": latency_ms,
            "vibe": vibe,
            "vibe_title": vibe_spec["title"],
            "chain_of_thought": {
                "step1_environmental_analysis": env_thought,
                "step2_sensory_missions": sensory_thought,
                "step3_navigation_math": nav_thought,
                "step4_screen_minimization": min_thought
            },
            "solar_metrics": solar_info,
            "turnaround_metrics": turnaround_info,
            "sensory_missions": sensory_missions,
            "field_card": field_card,
            "audio_script": audio_script,
            "waypoints": {
                "origin": {"lat": lat, "lon": lon, "name": location_name},
                "turnaround": {"lat": round(turnaround_lat, 6), "lon": round(turnaround_lon, 6)},
                "return_bearing_deg": round(return_bearing_deg, 1)
            },
            "system_health": {
                "ram_usage_mb": mem_status["process_ram_mb"],
                "system_ram_percent": mem_status["percent_system_ram_used"],
                "memory_safe": mem_status["memory_safe"],
                "neural_model_loaded": local_engine.is_loaded
            }
        }


# Global Reasoner Singleton
cot_reasoner = WalkBackerReasoner()
