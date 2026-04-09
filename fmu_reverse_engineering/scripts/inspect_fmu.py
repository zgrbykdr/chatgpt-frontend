import argparse

from fmu_reverse_engineering.fmu.inspector import FMUInspector

parser = argparse.ArgumentParser()
parser.add_argument('--fmu', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()

inspector = FMUInspector()
meta = inspector.inspect(args.fmu)
path = inspector.export_manifest(meta, args.out)
print(path)
