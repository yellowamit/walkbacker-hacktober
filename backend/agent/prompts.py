"""
Chain of Thought (CoT) Prompts & Templates for WalkBacker
Guides open-weight models through multi-stage outdoor expedition reasoning.
"""

COT_SYSTEM_PROMPT = """You are WalkBacker, an autonomous outdoor nature agent and expedition navigator designed for the 'Touch Grass' challenge.
Your core mission is to minimize screen time and maximize physical sensory engagement with the natural world.

When planning an outdoor expedition, you MUST follow this strict 4-stage Chain of Thought (CoT) reasoning protocol:

<thought_environment>
Analyze the current daylight window, solar elevation, autumn weather characteristics, and safe turnaround perimeter based on the user's available time.
</thought_environment>

<thought_sensory>
Formulate 3 distinct sensory touch-grass missions (auditory, tactile/botanical, observational) that get the user looking up at trees, listening to birds, or touching bark rather than staring at their phone screen.
</thought_sensory>

<thought_navigation>
Calculate the exact outbound turnaround time, maximum safe walking radius in kilometers, and reverse compass heading home.
</thought_navigation>

<thought_screen_minimization>
Synthesize a 30-second Pocket Field Card and concise spoken audio cues so the user can immediately pocket their device.
</thought_screen_minimization>
"""

VIBE_CATALOG = {
    "autumn_foliage": {
        "title": "Autumn Foliage & Canopy Hunt",
        "primary_mission": "Discover 3 contrasting leaf morphologies (lobed Oak vs palmate Maple vs serrated Beech).",
        "acoustic_cue": "Listen for dry marcescent leaves rustling in the canopy gusts.",
        "tactile_cue": "Feel the difference between smooth beech bark and deeply furrowed oak ridges.",
        "color_target": "Scarlet, amber, and saffron gold"
    },
    "mindful_birding": {
        "title": "Trailside Acoustic Birding & Silence",
        "primary_mission": "Locate a quiet perch 15 minutes outbound. Close eyes for 60 seconds and isolate 2 avian calls.",
        "acoustic_cue": "Identify Chickadee 'dee-dee-dee' or Nuthatch nasal 'yank-yank' calls.",
        "tactile_cue": "Feel the breeze on your neck to determine current prevailing wind direction.",
        "color_target": "Subtle plumage shades and bark camouflages"
    },
    "secret_greenway": {
        "title": "Micro-Adventure Urban Greenway",
        "primary_mission": "Traverse the nearest green corridor without checking any digital street map.",
        "acoustic_cue": "Track the sound of flowing brook water or wind through pine needles.",
        "tactile_cue": "Touch damp moss on the north side of rock outcroppings.",
        "color_target": "Emerald mosses, slate stone, fallen chestnuts"
    },
    "sunset_golden_hour": {
        "title": "Twilight Horizon & Golden Glow",
        "primary_mission": "Walk toward an open horizon line to witness the low-angled solar rays through tree branches.",
        "acoustic_cue": "Notice the evening chorus as diurnal songbirds settle into roosting trees.",
        "tactile_cue": "Notice the rapid temperature drop on your hands as the sun touches the horizon.",
        "color_target": "Warm copper, violet twilight, long tree shadows"
    }
}
