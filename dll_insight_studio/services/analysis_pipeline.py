from __future__ import annotations

from pathlib import Path
from typing import Any

from dll_insight_studio.analyzers.file_analyzer import FileAnalyzer
from dll_insight_studio.analyzers.function_classifier import FunctionClassificationEngine
from dll_insight_studio.analyzers.metadata_extractor import MetadataExtractor
from dll_insight_studio.analyzers.model_heuristics import ModelHeuristicEngine
from dll_insight_studio.analyzers.string_intelligence import StringIntelligenceEngine
from dll_insight_studio.analyzers.structural_mapper import StructuralMapper
from dll_insight_studio.analyzers.variable_inference import VariableInferenceEngine


class AnalysisPipeline:
    def __init__(self) -> None:
        self.file_analyzer = FileAnalyzer()
        self.metadata = MetadataExtractor()
        self.strings = StringIntelligenceEngine()
        self.structural = StructuralMapper()
        self.function_classifier = FunctionClassificationEngine()
        self.variable_engine = VariableInferenceEngine()
        self.model_engine = ModelHeuristicEngine()

    def run(self, dll_path: Path, manual_labels: dict[str, str] | None = None, function_overrides: dict[str, str] | None = None) -> dict[str, Any]:
        identity = self.file_analyzer.analyze(dll_path)
        metadata = self.metadata.extract(dll_path)
        classified_strings = self.strings.classify(metadata["strings"], manual_labels)
        structure = self.structural.map_structure(identity, metadata)
        functions = self.function_classifier.classify(structure["functions"], classified_strings, function_overrides)
        variables = self.variable_engine.infer(functions, classified_strings, identity)
        patterns = self.model_engine.rank_patterns(functions, classified_strings, identity)
        return {
            "identity": identity,
            "metadata": metadata,
            "strings": classified_strings,
            "structure": structure,
            "functions": functions,
            "variables": variables,
            "patterns": patterns,
        }
