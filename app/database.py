from __future__ import annotations

import csv
import json
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from .models import MusicRecord


class DatabaseError(Exception):
    """Veritabanı işlemleri sırasında oluşan özel hata."""


class MusicDatabase:
    """SQLite üzerinde tüm kayıt işlemlerini yöneten sınıf."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with closing(self._connect()) as conn, conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS music_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    baslik TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    aciklama TEXT DEFAULT '',
                    favori_mi INTEGER DEFAULT 0,
                    eklenme_tarihi TEXT NOT NULL,
                    son_acilis_tarihi TEXT,
                    etiketler TEXT DEFAULT ''
                )
                """
            )

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> MusicRecord:
        return MusicRecord(
            id=row["id"],
            baslik=row["baslik"],
            url=row["url"],
            aciklama=row["aciklama"],
            favori_mi=bool(row["favori_mi"]),
            eklenme_tarihi=row["eklenme_tarihi"],
            son_acilis_tarihi=row["son_acilis_tarihi"],
            etiketler=row["etiketler"],
        )

    def add_record(self, record: MusicRecord) -> int:
        try:
            with closing(self._connect()) as conn, conn:
                cursor = conn.execute(
                    """
                    INSERT INTO music_records
                    (baslik, url, aciklama, favori_mi, eklenme_tarihi, son_acilis_tarihi, etiketler)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.baslik,
                        record.url,
                        record.aciklama,
                        int(record.favori_mi),
                        record.eklenme_tarihi,
                        record.son_acilis_tarihi,
                        record.etiketler,
                    ),
                )
                return int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise DatabaseError("Bu YouTube linki zaten kayıtlı.") from exc

    def update_record(self, record: MusicRecord) -> None:
        if record.id is None:
            raise DatabaseError("Güncellenecek kayıt ID değeri içermiyor.")
        try:
            with closing(self._connect()) as conn, conn:
                conn.execute(
                    """
                    UPDATE music_records
                    SET baslik = ?, url = ?, aciklama = ?, favori_mi = ?, etiketler = ?
                    WHERE id = ?
                    """,
                    (
                        record.baslik,
                        record.url,
                        record.aciklama,
                        int(record.favori_mi),
                        record.etiketler,
                        record.id,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise DatabaseError("Bu YouTube linki zaten başka bir kayıtta var.") from exc

    def delete_record(self, record_id: int) -> None:
        with closing(self._connect()) as conn, conn:
            conn.execute("DELETE FROM music_records WHERE id = ?", (record_id,))

    def get_record(self, record_id: int) -> Optional[MusicRecord]:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM music_records WHERE id = ?", (record_id,)
            ).fetchone()
            return self._row_to_record(row) if row else None

    def search_records(
        self,
        query: str = "",
        only_favorites: bool = False,
        sort_by: str = "baslik",
    ) -> List[MusicRecord]:
        where_clauses = []
        params: list[str | int] = []

        if query:
            where_clauses.append("(LOWER(baslik) LIKE ? OR LOWER(aciklama) LIKE ? OR LOWER(etiketler) LIKE ?)")
            like_value = f"%{query.lower()}%"
            params.extend([like_value, like_value, like_value])

        if only_favorites:
            where_clauses.append("favori_mi = 1")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        order_sql = "ORDER BY baslik COLLATE NOCASE ASC"
        if sort_by == "son_acilan":
            order_sql = "ORDER BY (son_acilis_tarihi IS NULL), son_acilis_tarihi DESC, eklenme_tarihi DESC"

        query_sql = f"SELECT * FROM music_records {where_sql} {order_sql}"

        with closing(self._connect()) as conn:
            rows = conn.execute(query_sql, params).fetchall()
            return [self._row_to_record(row) for row in rows]

    def recent_opened(self, limit: int = 10) -> List[MusicRecord]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT * FROM music_records
                WHERE son_acilis_tarihi IS NOT NULL
                ORDER BY son_acilis_tarihi DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [self._row_to_record(row) for row in rows]

    def mark_opened_now(self, record_id: int) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "UPDATE music_records SET son_acilis_tarihi = ? WHERE id = ?",
                (now, record_id),
            )

    def export_json(self, output_path: Path, records: Iterable[MusicRecord]) -> None:
        payload = [record.__dict__ for record in records]
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_json(self, input_path: Path) -> int:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
        inserted = 0
        for item in raw:
            try:
                record = MusicRecord(
                    id=None,
                    baslik=item.get("baslik", ""),
                    url=item.get("url", ""),
                    aciklama=item.get("aciklama", ""),
                    favori_mi=bool(item.get("favori_mi", False)),
                    eklenme_tarihi=item.get("eklenme_tarihi") or datetime.now().isoformat(timespec="seconds"),
                    son_acilis_tarihi=item.get("son_acilis_tarihi"),
                    etiketler=item.get("etiketler", ""),
                )
                self.add_record(record)
                inserted += 1
            except DatabaseError:
                continue
        return inserted

    def export_csv(self, output_path: Path, records: Iterable[MusicRecord]) -> None:
        fieldnames = [
            "id",
            "baslik",
            "url",
            "aciklama",
            "favori_mi",
            "eklenme_tarihi",
            "son_acilis_tarihi",
            "etiketler",
        ]
        with output_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record.__dict__)

    def import_csv(self, input_path: Path) -> int:
        inserted = 0
        with input_path.open("r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for item in reader:
                try:
                    record = MusicRecord(
                        id=None,
                        baslik=item.get("baslik", ""),
                        url=item.get("url", ""),
                        aciklama=item.get("aciklama", ""),
                        favori_mi=item.get("favori_mi", "0") in {"1", "True", "true"},
                        eklenme_tarihi=item.get("eklenme_tarihi") or datetime.now().isoformat(timespec="seconds"),
                        son_acilis_tarihi=item.get("son_acilis_tarihi") or None,
                        etiketler=item.get("etiketler", ""),
                    )
                    self.add_record(record)
                    inserted += 1
                except DatabaseError:
                    continue
        return inserted

    def backup_database(self, output_path: Path) -> None:
        shutil.copy2(self.db_path, output_path)
