"""
Offline Nature & Flora Identification Engine
Performs trait keying, morphological feature matching, and colorimetric analysis.
Requires zero internet connection and consumes < 20MB of RAM.
"""
from typing import Dict, List, Optional
import re
from .taxonomy_db import SPECIES_CATALOG


class OfflineNatureIdentifier:
    """
    Lightweight, deterministic feature classifier and morphological matcher.
    """
    def __init__(self):
        self.catalog = SPECIES_CATALOG

    def identify_by_traits(self,
                           leaf_shape: Optional[str] = None,
                           color: Optional[str] = None,
                           category: Optional[str] = None,
                           bark_texture: Optional[str] = None,
                           habitat: Optional[str] = None) -> List[Dict]:
        """
        Multi-attribute morphological scoring key.
        """
        candidates = []

        for item in self.catalog:
            score = 0
            matches = []

            # Filter by broad category if provided
            if category and item["category"] != category:
                continue

            # Leaf shape matching
            if leaf_shape:
                item_shape = item["leaf_shape"].lower()
                for token in leaf_shape.lower().split():
                    if len(token) > 2 and token in item_shape:
                        score += 3
                        matches.append(f"Leaf shape matches '{token}'")

            # Color matching
            if color:
                item_color = item["autumn_color"].lower()
                for token in color.lower().split():
                    if len(token) > 2 and token in item_color:
                        score += 2.5
                        matches.append(f"Color profile matches '{token}'")

            # Bark texture matching
            if bark_texture:
                item_bark = item["bark_texture"].lower()
                for token in bark_texture.lower().split():
                    if len(token) > 2 and token in item_bark:
                        score += 2
                        matches.append(f"Bark texture aligns with '{token}'")

            # Habitat matching
            if habitat:
                item_hab = item["habitat"].lower()
                for token in habitat.lower().split():
                    if len(token) > 2 and token in item_hab:
                        score += 1.5
                        matches.append(f"Habitat environment aligns with '{token}'")

            # Calculate normalized confidence
            max_possible = 9.0
            confidence = min(0.98, max(0.20, score / max_possible)) if score > 0 else 0.15

            if score > 0:
                candidates.append({
                    "species": item,
                    "confidence": round(confidence, 2),
                    "score": score,
                    "matching_features": list(set(matches))
                })

        # Sort by confidence descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:3]

    def identify_from_text(self, text_query: str) -> Dict:
        """
        Natural language keying from a hiker's trail observation.
        e.g., 'Found a large orange mushroom on a rotting oak tree' or
              'Red pointed leaf with 7 lobes and acorns on the ground'
        """
        tokens = set(re.findall(r"\w+", text_query.lower()))
        best_match = None
        best_score = 0
        feature_traces = []

        for item in self.catalog:
            corpus = f"{item['common_name']} {item['scientific_name']} {item['autumn_color']} {item['leaf_shape']} {item['bark_texture']} {item['habitat']} {item['touch_grass_cue']}".lower()
            matched_words = [t for t in tokens if len(t) > 3 and t in corpus]
            score = len(matched_words)

            if score > best_score:
                best_score = score
                best_match = item
                feature_traces = matched_words

        if best_match and best_score >= 1:
            confidence = min(0.96, round(0.40 + (best_score * 0.12), 2))
            return {
                "identified": True,
                "confidence": confidence,
                "species": best_match,
                "reasoning": f"Identified {best_match['common_name']} based on trail observation traits: {', '.join(feature_traces[:4])}.",
                "touch_grass_action": best_match["touch_grass_cue"],
                "ecological_lore": best_match["ecological_note"]
            }

        # Fallback to top species with educational observation guidance
        default_species = self.catalog[0]
        return {
            "identified": False,
            "confidence": 0.35,
            "species": default_species,
            "reasoning": "Observation traits were partially ambiguous. Check leaf margin, bark furrowing, or fruit.",
            "touch_grass_action": "Pick up a specimen leaf and check if sinuses are U-shaped (Maple) or V-shaped (Oak).",
            "ecological_lore": default_species["ecological_note"]
        }


# Global singleton instance
nature_identifier = OfflineNatureIdentifier()
