import importlib
import sys
from types import SimpleNamespace


def test_extract_version_handles_nested_fileinfo_lists() -> None:
    sys.modules.setdefault("pefile", SimpleNamespace(PE=object))
    module = importlib.import_module("dll_insight_studio.analyzers.metadata_extractor")
    extractor = module.MetadataExtractor()
    pe = SimpleNamespace(
        FileInfo=[
            [
                SimpleNamespace(
                    Key=b"StringFileInfo",
                    StringTable=[SimpleNamespace(entries={b"CompanyName": b"Acme", b"FileVersion": b"1.2.3"})],
                )
            ]
        ]
    )

    result = extractor._extract_version(pe)  # noqa: SLF001

    assert result["CompanyName"] == "Acme"
    assert result["FileVersion"] == "1.2.3"
