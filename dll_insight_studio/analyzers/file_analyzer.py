from __future__ import annotations

from pathlib import Path
from typing import Any

import pefile


class FileAnalyzer:
    def analyze(self, dll_path: Path) -> dict[str, Any]:
        pe = pefile.PE(str(dll_path), fast_load=False)
        machine = pe.FILE_HEADER.Machine
        arch = "x64" if machine == 0x8664 else "x86" if machine == 0x14C else hex(machine)
        is_dll = bool(pe.FILE_HEADER.Characteristics & 0x2000)
        has_clr = hasattr(pe, "DIRECTORY_ENTRY_COM_DESCRIPTOR")
        detected_type = ".NET DLL" if has_clr else "Native DLL"
        protection_signals = []
        section_names = [s.Name.decode(errors="ignore").strip("\x00").lower() for s in pe.sections]
        packed_markers = ["upx", "aspack", "themida", "vmp"]
        if any(any(marker in name for marker in packed_markers) for name in section_names):
            protection_signals.append("Section name suggests packer/protector")
        if sum(s.get_entropy() > 7.3 for s in pe.sections) >= 2:
            protection_signals.append("High entropy sections suggest compression or protection")

        confidence = 0.95 if has_clr or is_dll else 0.6
        if protection_signals:
            confidence -= 0.1

        return {
            "path": str(dll_path),
            "architecture": arch,
            "is_dll": is_dll,
            "is_dotnet": has_clr,
            "dll_type": detected_type,
            "mixed_mode_or_uncertain": has_clr and any("native" in n for n in section_names),
            "protection_signals": protection_signals,
            "confidence": max(0.1, min(confidence, 0.99)),
        }
