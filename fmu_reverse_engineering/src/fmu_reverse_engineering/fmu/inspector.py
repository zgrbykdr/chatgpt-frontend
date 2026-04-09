from dataclasses import dataclass
from pathlib import Path

from fmu_reverse_engineering.domain.schemas.fmu_schema import FMUSchema


@dataclass
class FMUInspector:
    """Extract metadata from an FMU archive (starter placeholder)."""

    def inspect(self, fmu_path: str) -> FMUSchema:
        # Placeholder implementation: production version should parse modelDescription.xml
        return FMUSchema(
            fmu_path=fmu_path,
            fmi_version="unknown",
            fmu_type="unknown",
            variables=[],
            dependencies={},
        )

    def export_manifest(self, metadata: FMUSchema, output_dir: str) -> Path:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        manifest = out / "fmu_manifest.json"
        manifest.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
        return manifest
