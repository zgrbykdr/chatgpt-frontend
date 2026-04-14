from __future__ import annotations

import json
from collections import defaultdict

from .models import KNOWN_INPUTS, KNOWN_OUTPUTS, VariableRecord


class VariableMappingEngine:
    def build_mapping(self, xml_vars: list[VariableRecord], interface_candidates: list) -> list[dict]:
        fn_by_name = defaultdict(list)
        for c in interface_candidates:
            fn_by_name[c.function_name].append(c.dll_name)

        mappings: list[dict] = []
        seen = set()
        for v in xml_vars:
            if v.name in seen:
                continue
            seen.add(v.name)
            category = v.category
            if v.name in KNOWN_INPUTS:
                category = "input"
            elif v.name in KNOWN_OUTPUTS:
                category = "output"
            related_functions = [fn for fn in fn_by_name if any(k.lower().replace("side", "") in fn.lower() for k in ["Calculate", "Get", "Set", "Fluid"])][:5]
            mappings.append(
                {
                    "canonical_name": v.name,
                    "aliases": json.dumps([v.name]),
                    "category": category,
                    "confidence": v.confidence,
                    "related_dll": ",".join(sorted({dll for fns in fn_by_name.values() for dll in fns})),
                    "related_functions": json.dumps(related_functions),
                    "data_type": v.dtype,
                    "domain": v.domain or "",
                    "sweepable": 1 if category in {"input", "operating_input", "configuration"} else 0,
                }
            )
        return mappings
