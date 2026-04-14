from dll_insight_studio.analyzers.string_intelligence import StringIntelligenceEngine, is_meaningful_text


def test_classification_and_manual_override() -> None:
    engine = StringIntelligenceEngine()
    values = ["input_speed", "solver_step", "C:/temp/data.ini", "unknown"]
    result = engine.classify(values, {"unknown": "Possible Parameters"})
    cats = {r["value"]: r["category"] for r in result}
    assert cats["input_speed"] == "Possible Inputs"
    assert cats["solver_step"] == "Solver Terms"
    assert cats["unknown"] == "Possible Parameters"


def test_noise_strings_are_filtered() -> None:
    engine = StringIntelligenceEngine()
    result = engine.classify(["A_^A\\", "valid_input_name"])
    cats = {r["value"]: r["category"] for r in result}
    assert cats["A_^A\\"] == "Noise/Encoded"
    assert is_meaningful_text("A_^A\\") is False
