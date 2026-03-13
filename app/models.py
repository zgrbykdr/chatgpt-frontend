from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MusicRecord:
    """Veritabanındaki müzik kaydını temsil eder."""

    id: Optional[int]
    baslik: str
    url: str
    aciklama: str
    favori_mi: bool
    eklenme_tarihi: str
    son_acilis_tarihi: Optional[str]
    etiketler: str
