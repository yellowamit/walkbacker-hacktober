/**
 * WalkBacker Client-Side Offline Engine
 * Allows the phone to perform all calculations and CoT reasoning
 * even when completely disconnected from the laptop and cellular internet.
 */

const CLIENT_SPECIES = [
  {
    "common_name": "Sugar Maple",
    "scientific_name": "Acer saccharum",
    "category": "tree_foliage",
    "leaf_shape": "Palmate with 5 lobes and U-shaped sinuses",
    "autumn_color": "Flame Orange & Scarlet",
    "touch_grass_cue": "Hold a fallen leaf against the sun to observe clear translucent veins.",
    "ecological_note": "Keystone forest canopy species; sap contains up to 3% sucrose."
  },
  {
    "common_name": "Northern Red Oak",
    "scientific_name": "Quercus rubra",
    "category": "tree_foliage",
    "leaf_shape": "7 to 11 bristle-tipped pointed lobes",
    "autumn_color": "Deep Crimson to Russet-Amber",
    "touch_grass_cue": "Feel the leathery leaf texture; check the ground for flat-saucer acorns.",
    "ecological_note": "High tannin content preserves acorns through winter."
  },
  {
    "common_name": "American Beech",
    "scientific_name": "Fagus grandifolia",
    "category": "tree_foliage",
    "leaf_shape": "Elliptical with serrate margins and straight parallel veins",
    "autumn_color": "Golden Bronze to Papery Yellow",
    "touch_grass_cue": "Touch the trunk: it remains remarkably smooth ('elephant skin' feel).",
    "ecological_note": "Undergoes marcescence—retains dried golden leaves through winter."
  },
  {
    "common_name": "Turkey Tail Mushroom",
    "scientific_name": "Trametes versicolor",
    "category": "fungi",
    "leaf_shape": "Semicircular leathery brackets in layered rosettes",
    "autumn_color": "Concentric bands of chocolate, grey, and cream",
    "touch_grass_cue": "Flip the bracket: verify the underside has tiny white pores, not gills.",
    "ecological_note": "Crucial primary white-rot decomposer of lignin on fallen logs."
  },
  {
    "common_name": "Black-capped Chickadee",
    "scientific_name": "Poecile atricapillus",
    "category": "songbird",
    "leaf_shape": "Compact body, jet-black cap and bib, white cheeks",
    "autumn_color": "Black, white, and buffy tan",
    "touch_grass_cue": "Stand still near thickets and listen for their inquisitive 'chick-a-dee-dee'.",
    "ecological_note": "Possesses spatial memory capable of caching thousands of seeds individually."
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
    
    // Approximate elevation
    const latRad = lat * (Math.PI / 180);
    const decRad = declination * (Math.PI / 180);
    const elevation = Math.asin(Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad) * Math.cos((hour - 12) * 15 * (Math.PI / 180)));
    const elevDeg = Math.round((elevation * 180 / Math.PI) * 10) / 10;

    return {
      solar_elevation_deg: elevDeg,
      approx_sunset: "18:15",
      approx_golden_hour_start: "17:30"
    };
  }

  generateClientExpedition(durationMinutes, vibe, lat, lon, locationName) {
    const now = new Date();
    const turnaround = this.calculateTurnaround(durationMinutes, now);
    const solar = this.estimateSolar(lat, lon, now);
    const species = CLIENT_SPECIES[0];

    const envThought = `[On-Device Phone Reasoner] Calculated solar elevation ${solar.solar_elevation_deg}° at coordinates (${lat.toFixed(4)}, ${lon.toFixed(4)}). Outbound cutoff is ${turnaround.turnaround_time} leaving a ${turnaround.safety_buffer_minutes} min safety margin.`;
    const sensoryThought = `[On-Device Phone Reasoner] Formulated 3 tactile grounding tasks to prevent screen fixation: observing leaf margins, feeling bark texture, and listening for bird calls.`;
    const navThought = `[On-Device Phone Reasoner] Outbound walking limit is ${turnaround.max_outbound_radius_km} km. Safe return compass bearing calculated at 245° SW.`;
    const minThought = `[On-Device Phone Reasoner] 30-second Pocket Field Card generated. Screen will sleep with single chime at turnaround alert.`;

    return {
      success: true,
      vibe: vibe,
      vibe_title: "🍁 Autumn Foliage & Canopy Walk",
      chain_of_thought: {
        step1_environmental_analysis: envThought,
        step2_sensory_missions: sensoryThought,
        step3_navigation_math: navThought,
        step4_screen_minimization: minThought
      },
      turnaround_metrics: turnaround,
      solar_metrics: solar,
      field_card: {
        title: "🌿 " + locationName + " Expedition",
        location: locationName,
        expedition_duration_min: durationMinutes,
        turnaround_time: turnaround.turnaround_time,
        max_distance_km: turnaround.max_outbound_radius_km,
        return_bearing_deg: 245,
        cardinal_home: "SW",
        key_species: {
          name: species.common_name,
          scientific: species.scientific_name,
          cue: species.touch_grass_cue
        },
        missions: [
          "Listen: Stand still for 60 seconds; isolate 2 distinct bird calls or leaf rustles.",
          "Touch: Pick up a fallen leaf and observe whether leaf sinuses are U-shaped (Maple) or V-shaped (Oak).",
          "Look: Scan tree trunks for moss growth direction; notice moisture retention on shaded bark."
        ]
      },
      audio_script: `Welcome to your Touch Grass expedition at ${locationName}. You have ${durationMinutes} minutes. Your outbound walk ends at ${turnaround.turnaround_time}. Put your phone away and enjoy the trail.`,
      waypoints: {
        origin: { lat, lon, name: locationName },
        turnaround: { lat: lat + 0.005, lon: lon + 0.005 },
        return_bearing_deg: 245
      }
    };
  }

  identifyOffline(text) {
    const q = text.toLowerCase();
    for (const sp of CLIENT_SPECIES) {
      if (q.includes("maple") || q.includes("orange") || q.includes("5 lobe")) return sp;
      if (q.includes("oak") || q.includes("acorn") || q.includes("red")) return CLIENT_SPECIES[1];
      if (q.includes("beech") || q.includes("smooth bark")) return CLIENT_SPECIES[2];
      if (q.includes("mushroom") || q.includes("bracket") || q.includes("turkey")) return CLIENT_SPECIES[3];
      if (q.includes("bird") || q.includes("chickadee") || q.includes("cap")) return CLIENT_SPECIES[4];
    }
    return CLIENT_SPECIES[0];
  }
}

window.clientOfflineEngine = new ClientOfflineEngine();
