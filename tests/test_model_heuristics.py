from dll_insight_studio.analyzers.model_heuristics import ModelHeuristicEngine


def test_pattern_ranking_prefers_solver_when_terms_exist() -> None:
    engine = ModelHeuristicEngine()
    functions = [{"name": "compute_solver", "role": {"primary": "Compute"}}]
    strings = [{"value": "solver jacobian", "category": "Solver Terms", "confidence": 0.9}]
    ranked = engine.rank_patterns(functions, strings, {"is_dotnet": False})
    assert ranked[0]["confidence"] >= ranked[-1]["confidence"]
    assert any("solver" in p["pattern"] for p in ranked[:3])
