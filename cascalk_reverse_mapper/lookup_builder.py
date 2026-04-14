from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


class LookupBuilder:
    def generate_samples(self, axes: dict[str, tuple[float, float, int]], model_fn, sparse: bool = False) -> pd.DataFrame:
        values = []
        keys = list(axes)
        if sparse and len(keys) > 2:
            n = 200
            for _ in range(n):
                point = {k: float(np.random.uniform(v[0], v[1])) for k, v in axes.items()}
                point.update(model_fn(point))
                values.append(point)
            return pd.DataFrame(values)

        grids = [np.linspace(v[0], v[1], v[2]) for v in axes.values()]
        mesh = np.array(np.meshgrid(*grids)).T.reshape(-1, len(keys))
        for row in mesh:
            point = {k: float(row[idx]) for idx, k in enumerate(keys)}
            point.update(model_fn(point))
            values.append(point)
        return pd.DataFrame(values)

    def export(self, df: pd.DataFrame, out_dir: Path, name: str, metadata: dict) -> list[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base = out_dir / f"{name}_{stamp}"
        paths = []
        csv_p = base.with_suffix(".csv")
        df.to_csv(csv_p, index=False)
        paths.append(csv_p)
        json_p = base.with_suffix(".json")
        with json_p.open("w", encoding="utf-8") as f:
            json.dump({"metadata": metadata, "records": df.to_dict(orient="records")}, f, indent=2)
        paths.append(json_p)
        npz_p = base.with_suffix(".npz")
        np.savez(npz_p, **{c: df[c].to_numpy() for c in df.columns})
        paths.append(npz_p)
        try:
            h5_p = base.with_suffix(".h5")
            df.to_hdf(h5_p, key="lookup", mode="w")
            paths.append(h5_p)
        except Exception:
            pass
        return paths
