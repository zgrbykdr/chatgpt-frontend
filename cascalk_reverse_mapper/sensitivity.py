from __future__ import annotations

import pandas as pd


class SensitivityEngine:
    def influence_matrix(self, runs: list[dict], input_vars: list[str], output_vars: list[str]) -> pd.DataFrame:
        df = pd.DataFrame(runs)
        rows = []
        if df.empty:
            return pd.DataFrame(columns=["input_var", "output_var", "influence", "evidence_source", "notes"])
        for i in input_vars:
            for o in output_vars:
                if i in df and o in df:
                    influence = abs(df[[i, o]].corr().iloc[0, 1]) if len(df) > 1 else 0.0
                    if pd.isna(influence):
                        influence = 0.0
                    rows.append({"input_var": i, "output_var": o, "influence": float(influence), "evidence_source": "runtime_or_manual", "notes": "pearson abs corr"})
        return pd.DataFrame(rows).sort_values("influence", ascending=False)
