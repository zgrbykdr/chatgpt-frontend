from pathlib import Path


def test_module_entrypoint_file_exists() -> None:
    entry = Path("dll_insight_studio/__main__.py")
    assert entry.exists()
    assert "from dll_insight_studio.app import main" in entry.read_text(encoding="utf-8")
