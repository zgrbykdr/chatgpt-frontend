import argparse

import pandas as pd

from fmu_reverse_engineering.models import simple_models  # noqa: F401
from fmu_reverse_engineering.models.orchestration import ModelSearchEngine

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True)
args = parser.parse_args()

df = pd.read_parquet(args.dataset)
target = df.columns[-1]
x = df.drop(columns=[target])
y = df[target]

results = ModelSearchEngine(enabled_models=['constant', 'linear']).run(x, y, target)
print([r.model_dump() for r in results])
