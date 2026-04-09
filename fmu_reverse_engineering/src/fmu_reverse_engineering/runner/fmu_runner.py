from dataclasses import dataclass

import pandas as pd

from fmu_reverse_engineering.domain.schemas.experiment_schema import ExperimentPlanSchema


@dataclass
class FMURunner:
    """Simulation execution layer placeholder."""

    def run(self, plan: ExperimentPlanSchema) -> pd.DataFrame:
        # Placeholder: integrate with fmpy/PyFMI runtime in production.
        return pd.DataFrame([p.values for p in plan.points])
