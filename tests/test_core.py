from pathlib import Path
from threading import Thread

from cascalk_reverse_mapper.dll_analyzer import DLLAnalyzer
from cascalk_reverse_mapper.lookup_builder import LookupBuilder
from cascalk_reverse_mapper.package_scanner import PackageScanner
from cascalk_reverse_mapper.persistence import Persistence
from cascalk_reverse_mapper.sensitivity import SensitivityEngine
from cascalk_reverse_mapper.xml_extractor import XMLDomainExtractor


def test_package_scanner_classification(tmp_path: Path):
    root = tmp_path / "pkg"
    (root / "General/FLUID").mkdir(parents=True)
    (root / "PHE/Application").mkdir(parents=True)
    (root / "AlfaCalcInterface.dll").write_bytes(b"MZ" + b"\x00" * 200)
    (root / "PHE/Application/General_1phase.7235.application.xml").write_text("<Root InTempSide1='20' />")
    scanner = PackageScanner()
    recs = scanner.scan(root)
    assert any(r["role"] == "core_or_interface" for r in recs)
    assert any(r["kind"] == "xml" for r in recs)


def test_xml_extractor(tmp_path: Path):
    root = tmp_path
    (root / "PHE/Application").mkdir(parents=True)
    (root / "PHE/Application/General_1phase.7235.application.xml").write_text("<Root InTempSide1='20' HeatLoad='100' IsTwoPhase='false'/>")
    (root / "PHE/Views").mkdir(parents=True)
    (root / "PHE/Views/TotalView.xml").write_text("<View EffectiveArea='10'/>")
    (root / "General/FLUID").mkdir(parents=True)
    (root / "General/FLUID/water.fluid.xml").write_text("<Fluid Name='Water'/>")
    (root / "Settings.xml").write_text("<Settings CalcMode='1'/>")
    (root / "AvqAddin.xml").write_text("<Addin/>")
    vars_ = XMLDomainExtractor().parse_package(root)
    names = {v.name for v in vars_}
    assert "InTempSide1" in names
    assert "HeatLoad" in names


def test_dll_metadata_extraction(tmp_path: Path):
    dll = tmp_path / "AlfaCalcInterface.dll"
    data = bytearray(b"MZ" + b"\x00" * 300)
    data[0x3C:0x40] = (0x80).to_bytes(4, "little")
    if len(data) < 0x90:
        data.extend(b"\x00" * (0x90 - len(data)))
    data[0x84:0x86] = (0x8664).to_bytes(2, "little")
    dll.write_bytes(bytes(data) + b"Calculate\x00CreateItem\x00")
    res = DLLAnalyzer().analyze_dll(dll)
    assert res["architecture"] in {"x64", "machine_8664"}
    assert res["string_clue_count"] >= 1


def test_sensitivity_and_lookup_exports(tmp_path: Path):
    runs = [
        {"InTempSide1": 10.0, "HeatLoad": 100.0},
        {"InTempSide1": 20.0, "HeatLoad": 200.0},
    ]
    matrix = SensitivityEngine().influence_matrix(runs, ["InTempSide1"], ["HeatLoad"])
    assert not matrix.empty

    lb = LookupBuilder()
    df = lb.generate_samples({"InTempSide1": (10, 20, 3)}, lambda p: {"HeatLoad": p["InTempSide1"] * 2})
    out = lb.export(df, tmp_path, "lookup", {"axes": ["InTempSide1"]})
    assert any(p.suffix == ".csv" for p in out)


def test_sqlite_persistence(tmp_path: Path):
    db = Persistence(tmp_path / "db.sqlite3")
    db.execute("INSERT INTO projects(name, root_path) VALUES(?,?)", ("x", "/tmp"))
    count = db.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    assert count == 1


def test_sqlite_persistence_cross_thread(tmp_path: Path):
    db = Persistence(tmp_path / "db_thread.sqlite3")
    errors = []

    def worker():
        try:
            db.execute("INSERT INTO projects(name, root_path) VALUES(?,?)", ("threaded", "/tmp/thread"))
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    t = Thread(target=worker)
    t.start()
    t.join()

    assert not errors
    count = db.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    assert count == 1
