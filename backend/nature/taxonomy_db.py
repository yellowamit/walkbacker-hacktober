"""
Offline Botanical and Wildlife Taxonomy Database
Curated field data for temperate flora, autumn foliage, fungi, and songbirds.
Runs 100% offline with zero cloud latency.
"""
from typing import Dict, List, Optional

SPECIES_CATALOG: List[Dict] = [
    {
        "id": "sugar_maple",
        "common_name": "Sugar Maple",
        "scientific_name": "Acer saccharum",
        "category": "tree_foliage",
        "autumn_color": "Brilliant Flame Orange & Scarlet Red",
        "leaf_shape": "Palmate with 5 distinct blunt-pointed lobes and U-shaped sinuses",
        "bark_texture": "Greyish-brown with deep vertical furrows on mature trees",
        "habitat": "Rich mesic deciduous forests, upland slopes, parks",
        "touch_grass_cue": "Hold a fallen leaf against the sun to observe clear translucent veins.",
        "ecological_note": "Keystone forest canopy species; sap contains up to 3% sucrose."
    },
    {
        "id": "red_oak",
        "common_name": "Northern Red Oak",
        "scientific_name": "Quercus rubra",
        "category": "tree_foliage",
        "autumn_color": "Deep Crimson to Russet-Amber",
        "leaf_shape": "Alternate, 7 to 11 lobes with sharp bristle-tipped teeth and shallow sinuses",
        "bark_texture": "Dark grey with flat-topped ridges resembling ski tracks",
        "habitat": "Well-drained valley soils, woodland borders, parkland edges",
        "touch_grass_cue": "Feel the rigid leathery texture of the leaf; check the ground for shallow-saucer acorns.",
        "ecological_note": "Acorns mature in two years; high tannin content preserves them through winter."
    },
    {
        "id": "white_oak",
        "common_name": "White Oak",
        "scientific_name": "Quercus alba",
        "category": "tree_foliage",
        "autumn_color": "Wine Burgundy to Rich Chestnut Brown",
        "leaf_shape": "7 to 9 rounded finger-like lobes without bristle tips; deep finger-depth sinuses",
        "bark_texture": "Light ash-grey, scaly or shallowly fissured into loose vertical plates",
        "habitat": "Dry ridges to moist bottomlands; long-lived forest stalwarts",
        "touch_grass_cue": "Gently stroke the leaf edges—notice how soft and rounded they feel compared to red oak.",
        "ecological_note": "Can live over 400 years; supports over 500 species of native lepidoptera caterpillars."
    },
    {
        "id": "american_beech",
        "common_name": "American Beech",
        "scientific_name": "Fagus grandifolia",
        "category": "tree_foliage",
        "autumn_color": "Golden Bronze to Papery Parchment Yellow",
        "leaf_shape": "Simple, elliptical with straight parallel veins ending in small sharp teeth",
        "bark_texture": "Extremely smooth, unbroken light blue-grey ('elephant skin' feel)",
        "habitat": "Undisturbed mature woodlands, moist ravine slopes",
        "touch_grass_cue": "Touch the trunk: it remains remarkably smooth regardless of tree age. Leaves rustle dryly like paper.",
        "ecological_note": "Undergoes marcescence—retains dried golden leaves clinging to branches throughout winter."
    },
    {
        "id": "paper_birch",
        "common_name": "Paper Birch",
        "scientific_name": "Betula papyrifera",
        "category": "tree_foliage",
        "autumn_color": "Luminous Lemon Yellow",
        "leaf_shape": "Ovular to triangular, doubly serrate margins, pointed tip",
        "bark_texture": "Chalky white, peeling off in thin horizontal papery sheets with dark lenticels",
        "habitat": "Cool northern slopes, lake margins, forest disturbance clearings",
        "touch_grass_cue": "Gently feel the outer curled bark curls without peeling living bark off the tree.",
        "ecological_note": "Bark contains betulin, rendering it waterproof and naturally flammable even when damp."
    },
    {
        "id": "ginkgo",
        "common_name": "Ginkgo (Maidenhair Tree)",
        "scientific_name": "Ginkgo biloba",
        "category": "tree_foliage",
        "autumn_color": "Electric Saffron Yellow (Golden Carpet)",
        "leaf_shape": "Fan-shaped, two-lobed with dichotomously radiating veins (no midrib)",
        "bark_texture": "Grey-brown with deep furrowed ridges and corky fissures",
        "habitat": "Urban greenways, botanical gardens, park avenues",
        "touch_grass_cue": "Pick up a dropped leaf: notice the absence of a central vein; veins branch in continuous pairs.",
        "ecological_note": "Living fossil essentially unchanged for over 200 million years; survived the Permian-Triassic extinction."
    },
    {
        "id": "turkey_tail",
        "common_name": "Turkey Tail Mushroom",
        "scientific_name": "Trametes versicolor",
        "category": "fungi",
        "autumn_color": "Concentric rings of velvety russet, chocolate, slate grey, and cream",
        "leaf_shape": "Thin, leathery semicircular bracket fan (rosette clusters on rotting wood)",
        "bark_texture": "Velvety fine fuzz on top; tiny white pores (3-8 per mm) underneath",
        "habitat": "Decaying hardwood stumps, fallen logs, mossy forest floors",
        "touch_grass_cue": "Flip the bracket gently: verify the underside has microscopic white pores, not gills.",
        "ecological_note": "Crucial primary white-rot decomposer of lignin, recycling minerals back to topsoil."
    },
    {
        "id": "chicken_of_the_woods",
        "common_name": "Chicken of the Woods",
        "scientific_name": "Laetiporus sulphureus",
        "category": "fungi",
        "autumn_color": "Vibrant Neon Orange Cap with Bright Sulphur-Yellow Margins",
        "leaf_shape": "Layered overlapping brackets with thick fleshy lobes",
        "bark_texture": "Soft suede-like surface when fresh, chalky brittle when old",
        "habitat": "Dead or dying oaks, cherries, and standing hardwood snags",
        "touch_grass_cue": "Admire the incredible high-visibility contrast against dark forest bark.",
        "ecological_note": "Causes brown cubical rot in living heartwood; one of the most recognizable autumn forest fungi."
    },
    {
        "id": "black_capped_chickadee",
        "common_name": "Black-capped Chickadee",
        "scientific_name": "Poecile atricapillus",
        "category": "songbird",
        "autumn_color": "Jet-black cap and bib, clean white cheeks, buffy tan flanks",
        "leaf_shape": "Small plump body (12 cm), tiny chisel beak",
        "bark_texture": "Feathered; perches fearlessly on twig tips",
        "habitat": "Deciduous woodlands, park edges, willow thickets, garden feeders",
        "touch_grass_cue": "Stand still near a dense shrub and listen for their inquisitive 'chick-a-dee-dee-dee'.",
        "ecological_note": "Possesses spatial memory capable of caching thousands of seeds individually and retrieving them months later."
    },
    {
        "id": "white_breasted_nuthatch",
        "common_name": "White-breasted Nuthatch",
        "scientific_name": "Sitta carolinensis",
        "category": "songbird",
        "autumn_color": "Clean slate blue-grey back, bright white face and breast, black crown",
        "leaf_shape": "Compact body, short tail, slightly upturned slender bill",
        "bark_texture": "Tree trunk creeper; hops head-first downward along vertical bark",
        "habitat": "Mature deciduous trees, oak and maple woodlots",
        "touch_grass_cue": "Look vertically down tree trunks: they are the only common bird that routinely walks upside down.",
        "ecological_note": "Wedges large seeds into bark crevices and 'hatches' them open with bill strikes."
    },
    {
        "id": "american_robin",
        "common_name": "American Robin",
        "scientific_name": "Turdus migratorius",
        "category": "songbird",
        "autumn_color": "Warm terracotta brick-red breast, charcoal grey head and back, yellow bill",
        "leaf_shape": "Medium songbird, upright posture, alert posture",
        "bark_texture": "Runs and stops abruptly on lawn/leaf litter",
        "habitat": "Forest clearings, autumn berry shrubs, park lawns",
        "touch_grass_cue": "Listen for their sharp 'cheer-up, cheerily' morning song or leaf-shuffling in hedgerows.",
        "ecological_note": "Transitions in autumn from earthworm hunting to gorging on wild berries and sumac fruit."
    },
    {
        "id": "broadleaf_plantain",
        "common_name": "Broadleaf Plantain (White Man's Foot)",
        "scientific_name": "Plantago major",
        "category": "plant_herb",
        "autumn_color": "Deep Forest Green with tough fibrous ribs",
        "leaf_shape": "Broad oval rosette with 3 to 9 parallel, cord-like prominent veins",
        "bark_texture": "Smooth, thick, and resilient to heavy foot traffic",
        "habitat": "Compacted trail margins, park pathways, meadow footpaths",
        "touch_grass_cue": "Snap a leaf gently: notice the tough string-like veins pulling out like celery fibers.",
        "ecological_note": "Traditional soothing poultice for insect stings and scrapes on the trail."
    }
]


def search_species(query: str, category: Optional[str] = None) -> List[Dict]:
    """
    Search species database by keyword or category.
    """
    q = query.lower().strip()
    results = []
    for sp in SPECIES_CATALOG:
        if category and sp.get("category") != category:
            continue
        text_corpus = f"{sp['common_name']} {sp['scientific_name']} {sp['autumn_color']} {sp['leaf_shape']} {sp['habitat']}".lower()
        if q in text_corpus:
            results.append(sp)
    return results


def get_all_species() -> List[Dict]:
    """Return all cataloged species."""
    return SPECIES_CATALOG
