from __future__ import annotations
from typing import Dict, Any, List


def apply_mappings_to_feats(feats: List[Dict[str, Any]], mappings: List[Dict[str, Any]]) -> int:
    mapped_count = 0
    for mapping in mappings:
        feat_name = (mapping.get("featName") or "").strip().lower()
        feat_source = (mapping.get("source") or "").strip().lower()
        feat_id = mapping.get("featId")
        modifiers = mapping.get("modifiers", [])
        prerequisites = mapping.get("prerequisites", [])

        for feat in feats:
            same_id = bool(feat_id) and feat.get("id") == feat_id
            same_name_source = (
                feat.get("name", "").strip().lower() == feat_name
                and feat.get("source", "").strip().lower() == feat_source
            )
            if same_id or same_name_source:
                feat["mappingStatus"] = "Mapped"
                feat["modifiers"] = modifiers
                feat["prerequisites"] = prerequisites
                mapped_count += 1
    return mapped_count
