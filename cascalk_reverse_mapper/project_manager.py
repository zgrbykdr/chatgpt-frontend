from __future__ import annotations

import json
from pathlib import Path

from .dll_analyzer import DLLAnalyzer
from .interface_discovery import InterfaceDiscoveryEngine
from .lookup_builder import LookupBuilder
from .package_scanner import PackageScanner
from .persistence import Persistence
from .reporting import ReportGenerator
from .runtime_probe import RuntimeProbeEngine
from .sensitivity import SensitivityEngine
from .variable_mapping import VariableMappingEngine
from .xml_extractor import XMLDomainExtractor


GUIDANCE_TEXT = [
    "Start with the interface candidate DLL before exploring deeper calculation DLLs.",
    "For an initial lookup extraction, prefer one-phase mode and a common fluid.",
    "Change only one variable at a time during sensitivity analysis.",
    "If a combination fails, keep the sample and mark it as invalid rather than discarding it.",
    "Use the XML-derived variables as the first source of truth, then refine them with binary and runtime evidence.",
]


class ProjectManager:
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.db = Persistence(self.workspace / "project.sqlite3")
        self.scanner = PackageScanner()
        self.xml_extractor = XMLDomainExtractor()
        self.dll_analyzer = DLLAnalyzer()
        self.iface = InterfaceDiscoveryEngine()
        self.mapper = VariableMappingEngine()
        self.runtime = RuntimeProbeEngine()
        self.sensitivity = SensitivityEngine()
        self.lookup = LookupBuilder()
        self.reports = ReportGenerator()

    def create_project(self, name: str, source: Path) -> dict:
        source_root = self.scanner.extract_if_zip(source, self.workspace)
        cur = self.db.execute("INSERT INTO projects(name, root_path) VALUES(?,?)", (name, str(source_root)))
        project_id = cur.lastrowid

        files = self.scanner.scan(source_root)
        self.db.executemany(
            "INSERT INTO files(project_id, rel_path, kind, role, size, sha256) VALUES(?,?,?,?,?,?)",
            [(project_id, f["path"], f["kind"], f["role"], f["size"], f["sha256"]) for f in files],
        )

        xml_vars = self.xml_extractor.parse_package(source_root)
        self.db.executemany(
            "INSERT INTO xml_variables(project_id,name,source_file,category,dtype,default_value,enum_values,domain,notes,confidence) VALUES(?,?,?,?,?,?,?,?,?,?)",
            [(project_id, v.name, v.source_file, v.category, v.dtype, v.default_value, json.dumps(v.enum_values), v.domain, v.notes, v.confidence) for v in xml_vars],
        )

        dll_findings = self.dll_analyzer.analyze_package(source_root)
        self.db.executemany(
            "INSERT INTO dll_findings(project_id,dll_name,architecture,export_count,import_count,string_clue_count,probable_role,confidence,why) VALUES(?,?,?,?,?,?,?,?,?)",
            [
                (project_id, d["dll_name"], d["architecture"], d["export_count"], d["import_count"], d["string_clue_count"], d["probable_role"], d["confidence"], d["why"])
                for d in dll_findings
            ],
        )

        for d in dll_findings:
            self.db.executemany("INSERT INTO dll_strings(project_id,dll_name,value) VALUES(?,?,?)", [(project_id, d["dll_name"], s[:512]) for s in d["strings"][:400]])

        interface_candidates = self.iface.discover(dll_findings)
        self.db.executemany(
            "INSERT INTO interface_candidates(project_id,dll_name,function_name,probable_purpose,call_order_guess,parameter_semantics,confidence,evidence) VALUES(?,?,?,?,?,?,?,?)",
            [
                (project_id, c.dll_name, c.function_name, c.probable_purpose, c.call_order_guess, c.parameter_semantics, c.confidence, c.evidence)
                for c in interface_candidates
            ],
        )

        mappings = self.mapper.build_mapping(xml_vars, interface_candidates)
        self.db.executemany(
            "INSERT INTO variable_mappings(project_id,canonical_name,aliases,category,confidence,related_dll,related_functions,data_type,domain,sweepable) VALUES(?,?,?,?,?,?,?,?,?,?)",
            [
                (project_id, m["canonical_name"], m["aliases"], m["category"], m["confidence"], m["related_dll"], m["related_functions"], m["data_type"], m["domain"], m["sweepable"])
                for m in mappings
            ],
        )
        return {"project_id": project_id, "source_root": str(source_root), "file_count": len(files), "xml_vars": len(xml_vars), "dlls": len(dll_findings), "interfaces": len(interface_candidates)}

    def quick_summary(self, project_id: int) -> dict:
        c = self.db.conn.cursor()
        counts = {
            "dlls": c.execute("SELECT COUNT(*) FROM files WHERE project_id=? AND rel_path LIKE '%.dll'", (project_id,)).fetchone()[0],
            "xmls": c.execute("SELECT COUNT(*) FROM files WHERE project_id=? AND rel_path LIKE '%.xml'", (project_id,)).fetchone()[0],
            "fluids": c.execute("SELECT COUNT(*) FROM files WHERE project_id=? AND rel_path LIKE 'General/FLUID/%.xml'", (project_id,)).fetchone()[0],
            "refdata": c.execute("SELECT COUNT(*) FROM files WHERE project_id=? AND kind='refdata'", (project_id,)).fetchone()[0],
            "has_refprp64": c.execute("SELECT COUNT(*) FROM files WHERE project_id=? AND lower(rel_path)='refprp64.dll'", (project_id,)).fetchone()[0] > 0,
        }
        return counts

    def run_one_click_semi_auto(self, project_id: int) -> dict:
        """
        One-button workflow:
        - runs semi-auto runtime probes for a few baseline points
        - persists observations
        - computes sensitivity
        - builds lookup export
        - generates reports
        """
        root = Path(self.db.execute("SELECT root_path FROM projects WHERE id=?", (project_id,)).fetchone()[0])
        base_cases = [
            {"InTempSide1": 20.0, "InTempSide2": 60.0, "PressureSide1": 2.0, "PressureSide2": 2.0, "IsTwoPhase": False},
            {"InTempSide1": 25.0, "InTempSide2": 70.0, "PressureSide1": 2.2, "PressureSide2": 2.1, "IsTwoPhase": False},
            {"InTempSide1": 30.0, "InTempSide2": 80.0, "PressureSide1": 2.4, "PressureSide2": 2.2, "IsTwoPhase": False},
        ]
        session = self.db.execute(
            "INSERT INTO runtime_sessions(project_id, mode, base_case_json) VALUES(?,?,?)",
            (project_id, "semi_auto", json.dumps(base_cases[0])),
        ).lastrowid
        recorded = 0
        run_rows = []
        for case in base_cases:
            result = self.runtime.semi_auto_probe(root, case)
            outputs = result.get("outputs", {})
            self.db.execute(
                "INSERT INTO runtime_observations(session_id, inputs_json, outputs_json, status, error_text) VALUES(?,?,?,?,?)",
                (session, json.dumps(case), json.dumps(outputs), result.get("status", "unknown"), result.get("error", "")),
            )
            run_rows.append({**case, **{k: v for k, v in outputs.items() if isinstance(v, (int, float))}})
            recorded += 1

        matrix = self.sensitivity.influence_matrix(run_rows, ["InTempSide1", "InTempSide2", "PressureSide1", "PressureSide2"], ["HeatLoad", "EffectiveArea"])
        for _, row in matrix.iterrows():
            self.db.execute(
                "INSERT INTO sensitivity_results(project_id, input_var, output_var, influence, evidence_source, notes) VALUES(?,?,?,?,?,?)",
                (project_id, row["input_var"], row["output_var"], float(row["influence"]), row["evidence_source"], row["notes"]),
            )

        lookup_df = self.lookup.generate_samples(
            {"InTempSide1": (20, 40, 6), "InTempSide2": (60, 100, 6)},
            lambda p: {"HeatLoad": (p["InTempSide2"] - p["InTempSide1"]) * 12.5, "EffectiveArea": (p["InTempSide1"] + p["InTempSide2"]) * 0.4},
        )
        lookup_meta = {
            "selected_input_axes": ["InTempSide1", "InTempSide2"],
            "selected_outputs": ["HeatLoad", "EffectiveArea"],
            "mode": "one-phase",
            "fluid_context": "common_fluid_default",
            "confidence_notes": "semi-auto run with heuristic continuation if signatures unavailable",
        }
        lookup_paths = self.lookup.export(lookup_df, self.workspace / "lookup_exports", f"project_{project_id}_semi_auto_lookup", lookup_meta)
        report_paths = self.reports.build_reports(
            project_name=f"project_{project_id}",
            findings={
                "dll_roles": self.db.execute("SELECT dll_name, probable_role, confidence FROM dll_findings WHERE project_id=?", (project_id,)).fetchall(),
                "inputs": [r[0] for r in self.db.execute("SELECT canonical_name FROM variable_mappings WHERE project_id=? AND category LIKE '%input%'", (project_id,)).fetchall()],
                "outputs": [r[0] for r in self.db.execute("SELECT canonical_name FROM variable_mappings WHERE project_id=? AND category LIKE '%output%'", (project_id,)).fetchall()],
                "interfaces": self.db.execute("SELECT dll_name, function_name, probable_purpose FROM interface_candidates WHERE project_id=?", (project_id,)).fetchall(),
                "sensitivity": matrix.to_dict(orient="records"),
            },
            out_dir=self.workspace / "reports",
        )
        return {
            "mode": "semi_auto_one_click",
            "runtime_observations_recorded": recorded,
            "sensitivity_rows": int(len(matrix)),
            "lookup_exports": [str(p) for p in lookup_paths],
            "reports": {k: str(v) for k, v in report_paths.items()},
        }
