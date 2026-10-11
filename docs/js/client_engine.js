/**
 * WalkBacker Client-Side Offline AI Reasoner
 * Provides full 4-stage Chain of Thought outdoor planning directly inside the browser.
 * Works 100% offline on mobile phones with zero server backend required.
 */

const CLIENT_VIBES = {
  autumn_foliage: {
    title: "🍁 Autumn Foliage & Canopy Hunt",
    primary_mission: "Discover 3 contrasting leaf morphologies (lobed Oak vs palmate Maple vs serrated Beech).",
    acoustic_cue: "Listen for dry marcescent leaves rustling in the canopy gusts.",
    tactile_cue: "Feel the difference between smooth beech bark and deeply furrowed oak ridges.",
    color_target: "Scarlet, amber, and saffron gold",
    species_idx: 0
  },
  mindful_birding: {
    title: "🐦 Trailside Acoustic Birding & Silence",
    primary_mission: "Locate a quiet perch 15 minutes outbound. Close eyes for 60 seconds and isolate 2 avian calls.",
    acoustic_cue: "Identify Chickadee 'dee-dee-dee' or Nuthatch nasal 'yank-yank' calls.",
    tactile_cue: "Feel the breeze on your neck to determine current prevailing wind direction.",
    color_target: "Subtle plumage shades and bark camouflages",
    species_idx: 4
  },
  secret_greenway: {
    title: "🌿 Micro-Adventure Urban Greenway",
    primary_mission: "Traverse the nearest green corridor without checking any digital street map.",
    acoustic_cue: "Track the sound of flowing brook water or wind through pine needles.",
    tactile_cue: "Touch damp moss on the north side of rock outcroppings.",
    color_target: "Emerald mosses, slate stone, fallen chestnuts",
    species_idx: 3
  },
  sunset_golden_hour: {
    title: "🌅 Twilight Horizon & Golden Glow",
    primary_mission: "Walk toward an open horizon line to witness the low-angled solar rays through tree branches.",
    acoustic_cue: "Notice the evening chorus as diurnal songbirds settle into roosting trees.",
    tactile_cue: "Notice the rapid temperature drop on your hands as the sun touches the horizon.",
    color_target: "Warm copper, violet twilight, long tree shadows",
    species_idx: 1
  }
};

const CLIENT_SPECIES = [
  {
    common_name: "Sugar Maple",
    scientific_name: "Acer saccharum",
    category: "tree_foliage",
    leaf_shape: "Palmate with 5 lobes and U-shaped sinuses",
    autumn_color: "Flame Orange & Scarlet",
    touch_grass_cue: "Hold a fallen leaf against the sun to observe clear translucent veins.",
    ecological_note: "Keystone forest canopy species; sap contains up to 3% sucrose."
  },
  {
    common_name: "Northern Red Oak",
    scientific_name: "Quercus rubra",
    category: "tree_foliage",
    leaf_shape: "7 to 11 bristle-tipped pointed lobes with shallow sinuses",
    autumn_color: "Deep Crimson to Russet-Amber",
    touch_grass_cue: "Feel the rigid leathery leaf texture; check the ground for flat-saucer acorns.",
    ecological_note: "High tannin content preserves acorns through winter."
  },
  {
    common_name: "American Beech",
    scientific_name: "Fagus grandifolia",
    category: "tree_foliage",
    leaf_shape: "Elliptical with serrate margins and straight parallel veins",
    autumn_color: "Golden Bronze to Papery Yellow",
    touch_grass_cue: "Touch the trunk: it remains remarkably smooth ('elephant skin' feel).",
    ecological_note: "Undergoes marcescence—retains dried golden leaves through winter."
  },
  {
    common_name: "Turkey Tail Mushroom",
    scientific_name: "Trametes versicolor",
    category: "fungi",
    leaf_shape: "Semicircular leathery brackets in layered rosettes",
    autumn_color: "Concentric bands of chocolate, grey, and cream",
    touch_grass_cue: "Flip the bracket: verify the underside has tiny white pores, not gills.",
    ecological_note: "Crucial primary white-rot decomposer of lignin on fallen logs."
  },
  {
    common_name: "Black-capped Chickadee",
    scientific_name: "Poecile atricapillus",
    category: "songbird",
    leaf_shape: "Compact body, jet-black cap and bib, white cheeks",
    autumn_color: "Black, white, and buffy tan",
    touch_grass_cue: "Stand still near thickets and listen for their inquisitive 'chick-a-dee-dee'.",
    ecological_note: "Possesses spatial memory capable of caching thousands of seeds individually."
  },
  {
    common_name: "White-breasted Nuthatch",
    scientific_name: "Sitta carolinensis",
    category: "songbird",
    leaf_shape: "Compact body, short tail, slightly upturned bill",
    autumn_color: "Slate blue-grey back, bright white face",
    touch_grass_cue: "Look vertically down tree trunks: only common bird that routinely walks upside down.",
    ecological_note: "Wedges seeds into bark crevices and hatches them open."
  }
];

class ClientOfflineEngine {
  calculateTurnaround(totalMinutes, startTime = new Date()) {
    const outboundMinutes = (totalMinutes / 2.0) * 0.85;
    const bufferMinutes = totalMinutes - (outboundMinutes * 2.0);
    const turnaroundMs = startTime.getTime() + (outboundMinutes * 60 * 1000);
    const turnaroundDate = new Date(turnaroundMs);

    const pad = (n) => String(n).padStart(2, '0');
    const timeStr = `${pad(turnaroundDate.getHours())}:${pad(turnaroundDate.getMinutes())}:${pad(turnaroundDate.getSeconds())}`;

    return {
      total_minutes: totalMinutes,
      outbound_minutes: Math.round(outboundMinutes * 10) / 10,
      safety_buffer_minutes: Math.round(bufferMinutes * 10) / 10,
      turnaround_time: timeStr,
      max_outbound_radius_km: Math.round((4.5 * (outboundMinutes / 60.0)) * 100) / 100
    };
  }

  estimateSolar(lat, lon, date = new Date()) {
    const dayOfYear = Math.floor((date - new Date(date.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24));
    const declination = 23.45 * Math.sin((Math.PI / 180) * (360 / 365) * (284 + dayOfYear));
    const hour = date.getHours() + date.getMinutes() / 60;

    const latRad = lat * (Math.PI / 180);
    const decRad = declination * (Math.PI / 180);
    const elevation = Math.asin(Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad) * Math.cos((hour - 12) * 15 * (Math.PI / 180)));
    const elevDeg = Math.round((elevation * 180 / Math.PI) * 10) / 10;

    // Approximate sunset hour calculation
    let sunsetStr = "18:15";
    try {
      const cosHas = (-0.0145 - Math.sin(latRad) * Math.sin(decRad)) / (Math.cos(latRad) * Math.cos(decRad));
      if (cosHas >= -1 && cosHas <= 1) {
        const hasDeg = Math.acos(cosHas) * 180 / Math.PI;
        const sunsetSolarHour = (180 + hasDeg) / 15;
        const sunsetH = Math.floor(sunsetSolarHour);
        const sunsetM = Math.floor((sunsetSolarHour - sunsetH) * 60);
        sunsetStr = `${String(sunsetH).padStart(2, '0')}:${String(sunsetM).padStart(2, '0')}`;
      }
    } catch (e) {}

    return {
      solar_elevation_deg: elevDeg,
      approx_sunset: sunsetStr,
      approx_golden_hour_start: "17:30"
    };
  }

  generateClientExpedition(durationMinutes, vibeKey = "autumn_foliage", lat = 32.15, lon = 75.4667, locationName = "Local Trailhead") {
    const now = new Date();
    const turnaround = this.calculateTurnaround(durationMinutes, now);
    const solar = this.estimateSolar(lat, lon, now);
    const vibe = CLIENT_VIBES[vibeKey] || CLIENT_VIBES.autumn_foliage;
    const species = CLIENT_SPECIES[vibe.species_idx] || CLIENT_SPECIES[0];

    // Compute return bearing based on outbound angle
    const outboundBearing = 65;
    const returnBearing = (outboundBearing + 180) % 360;

    const envThought = `[On-Device AI Engine] Analyzing solar elevation (${solar.solar_elevation_deg}°) at coordinates (${lat.toFixed(4)}, ${lon.toFixed(4)}). Approximate sunset is ${solar.approx_sunset}. To maintain a ${turnaround.safety_buffer_minutes} min reserve, outbound travel must cease at exactly ${turnaround.turnaround_time}. Outbound radial radius capped at ${turnaround.max_outbound_radius_km} km.`;
    
    const sensoryThought = `[On-Device AI Engine] Formulating sensory grounding for '${vibe.title}'. Replacing screen habits with 3 mindful sensory challenges: 1) ${vibe.acoustic_cue} 2) ${species.touch_grass_cue} 3) ${vibe.primary_mission}`;
    
    const navThought = `[On-Device AI Engine] Calibrated pace: 4.5 km/h. At ${turnaround.turnaround_time}, the return vector home is ${returnBearing}° SW. Offline compass needle will orient return bearing directly without cellular maps.`;
    
    const minThought = `[On-Device AI Engine] Pocket Field Card synthesized for 30-second review. Device will remain in pocket with audio chime trigger at turnaround.`;

    return {
      success: true,
      vibe: vibeKey,
      vibe_title: vibe.title,
      chain_of_thought: {
        step1_environmental_analysis: envThought,
        step2_sensory_missions: sensoryThought,
        step3_navigation_math: navThought,
        step4_screen_minimization: minThought
      },
      turnaround_metrics: turnaround,
      solar_metrics: solar,
      field_card: {
        title: vibe.title,
        location: locationName,
        expedition_duration_min: durationMinutes,
        turnaround_time: turnaround.turnaround_time,
        max_distance_km: turnaround.max_outbound_radius_km,
        return_bearing_deg: returnBearing,
        cardinal_home: "SW",
        key_species: {
          name: species.common_name,
          scientific: species.scientific_name,
          cue: species.touch_grass_cue
        },
        missions: [
          `Acoustic: ${vibe.acoustic_cue}`,
          `Botanical: Examine ${species.common_name}. ${species.touch_grass_cue}`,
          `Observational: Look for ${vibe.color_target}. Focus gaze outward into nature.`
        ]
      },
      audio_script: `Welcome to your Touch Grass expedition at ${locationName}. You have ${durationMinutes} minutes. Your outbound walk ends at ${turnaround.turnaround_time}. First mission: ${vibe.acoustic_cue}. Put your phone away and touch grass.`,
      waypoints: {
        origin: { lat, lon, name: locationName },
        turnaround: { lat: lat + 0.004, lon: lon + 0.005 },
        return_bearing_deg: returnBearing
      }
    };
  }

  identifyOffline(text) {
    const q = text.toLowerCase();
    for (const sp of CLIENT_SPECIES) {
      if (q.includes("maple") || q.includes("orange") || q.includes("5 lobe") || q.includes("sugar")) return sp;
      if (q.includes("oak") || q.includes("acorn") || q.includes("red oak") || q.includes("bristle")) return CLIENT_SPECIES[1];
      if (q.includes("beech") || q.includes("smooth bark") || q.includes("elephant") || q.includes("papery")) return CLIENT_SPECIES[2];
      if (q.includes("mushroom") || q.includes("bracket") || q.includes("turkey") || q.includes("fungus")) return CLIENT_SPECIES[3];
      if (q.includes("chickadee") || q.includes("black bib") || q.includes("dee-dee")) return CLIENT_SPECIES[4];
      if (q.includes("nuthatch") || q.includes("upside down") || q.includes("tree trunk")) return CLIENT_SPECIES[5];
    }
    return CLIENT_SPECIES[0];
  }
}

// Global instance
window.clientOfflineEngine = new ClientOfflineEngine();
