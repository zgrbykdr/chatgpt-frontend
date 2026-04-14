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

    assert deps[0]["library"] == "KERNEL32.dll"
    assert "42" in consts["numeric_constants"]
    assert any("fmi2SetReal" in row["name"] for row in fmu)
    assert any(row["parameter"] == "param_heat_coeff" for row in doe)
