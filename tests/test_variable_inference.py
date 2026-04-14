from dll_insight_studio.analyzers.variable_inference import VariableInferenceEngine


def test_variable_inference_skips_noise_strings() -> None:
    engine = VariableInferenceEngine()
    functions = [{"name": "compute_main"}]
    strings = [
        {"value": "A_^A\\", "category": "Possible Inputs", "confidence": 0.8},
        {"value": "mass_flow_input", "category": "Possible Inputs", "confidence": 0.8},
    ]
    out = engine.infer(functions, strings, {"is_dotnet": False})
    names = {v["name"] for v in out}
    assert "mass_flow_input" in names or any(n.startswith("var_") for n in names)
    assert all("A_^A" not in n for n in names)
