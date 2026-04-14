from pathlib import Path

from dll_insight_studio.analyzers.reverse_engineering import ReverseEngineeringEnhancer


def test_reverse_engineering_builds_fmu_lookup_and_doe() -> None:
    enhancer = ReverseEngineeringEnhancer()
    metadata = {
        "imports": [
            {"library": "KERNEL32.dll", "name": "CreateFileW"},
            {"library": "KERNEL32.dll", "name": "ReadFile"},
        ],
        "numeric_constants": ["0.1", "42"],
    }
    strings = [
        {"value": "fmi2SetReal", "category": "FMI/FMU Terms", "confidence": 0.9},
        {"value": "alpha=1.5e-3", "category": "Numeric/Scientific Terms", "confidence": 0.6},
    ]
    variables = [
        {"name": "input_mass_flow", "category": "input", "region": "offset_group_1", "confidence": 0.8},
        {"name": "param_heat_coeff", "category": "parameter", "region": "offset_group_2", "confidence": 0.7},
    ]

    deps = enhancer.build_dependency_map(metadata)
    consts = enhancer.extract_constants(metadata, strings)
    fmu = enhancer.build_fmu_lookup_table(strings, variables)
    doe = enhancer.build_doe_plan(variables)
    ranges = enhancer.infer_parameter_ranges(strings, variables)

    assert deps[0]["library"] == "KERNEL32.dll"
    assert deps[0]["is_system"] is True
    assert "42" in consts["numeric_constants"]
    assert any("fmi2SetReal" in row["name"] for row in fmu)
    assert any(row["parameter"] == "param_heat_coeff" for row in doe)
    assert any(r["name"] == "param_heat_coeff" for r in ranges)


def test_dymola_lookup_csv_export(tmp_path: Path) -> None:
    enhancer = ReverseEngineeringEnhancer()
    out = enhancer.export_dymola_lookup_csv(
        [{"name": "param_heat_coeff", "category": "parameter", "region": "offset", "confidence": 0.8, "min": 0, "max": 10, "default": 5, "source": "test"}],
        tmp_path / "dymola_lookup_table.csv",
    )
    content = out.read_text(encoding="utf-8")
    assert "param_heat_coeff" in content
    assert "min,max,default" in content


def test_dependency_auto_resolution(tmp_path: Path) -> None:
    enhancer = ReverseEngineeringEnhancer()
    dep_file = tmp_path / "CasCalc.dll"
    dep_file.write_text("x", encoding="utf-8")
    dependencies = [
        {"library": "CasCalc.dll", "is_system": False},
        {"library": "KERNEL32.dll", "is_system": True},
        {"library": "Missing.dll", "is_system": False},
    ]
    resolved, missing = enhancer.resolve_dependency_paths(dependencies, [tmp_path])
    assert "CasCalc.dll" in resolved
    assert "Missing.dll" in missing
