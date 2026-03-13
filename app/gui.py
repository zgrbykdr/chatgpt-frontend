from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .database import DatabaseError, MusicDatabase
from .edge_launcher import EdgeLaunchError, open_url_in_edge
from .models import MusicRecord
from .settings_manager import SettingsManager, guess_edge_path, guess_edge_profile_path


class MusicDialog(QDialog):
    """Yeni kayıt ekleme ve düzenleme penceresi."""

    def __init__(self, parent: QWidget | None = None, record: Optional[MusicRecord] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Müzik Kaydı")
        self.setModal(True)
        self.resize(460, 340)

        self.baslik_input = QLineEdit()
        self.url_input = QLineEdit()
        self.aciklama_input = QTextEdit()
        self.etiketler_input = QLineEdit()
        self.favori_checkbox = QCheckBox("Favori")

        form = QFormLayout()
        form.addRow("Müzik Adı:", self.baslik_input)
        form.addRow("YouTube Linki:", self.url_input)
        form.addRow("Etiketler (virgül ile):", self.etiketler_input)
        form.addRow("Açıklama / Not:", self.aciklama_input)
        form.addRow("", self.favori_checkbox)

        kaydet_button = QPushButton("Kaydet")
        iptal_button = QPushButton("İptal")
        kaydet_button.clicked.connect(self.accept)
        iptal_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(kaydet_button)
        buttons.addWidget(iptal_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

        if record:
            self.baslik_input.setText(record.baslik)
            self.url_input.setText(record.url)
            self.etiketler_input.setText(record.etiketler)
            self.aciklama_input.setPlainText(record.aciklama)
            self.favori_checkbox.setChecked(record.favori_mi)

    def values(self) -> dict:
        return {
            "baslik": self.baslik_input.text().strip(),
            "url": self.url_input.text().strip(),
            "aciklama": self.aciklama_input.toPlainText().strip(),
            "etiketler": self.etiketler_input.text().strip(),
            "favori_mi": self.favori_checkbox.isChecked(),
        }


class SettingsDialog(QDialog):
    """Edge yolu/profili gibi ayarların düzenlendiği pencere."""

    def __init__(self, settings: SettingsManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Ayarlar")
        self.resize(560, 260)

        self.edge_path_input = QLineEdit(settings.get("edge_path"))
        self.profile_path_input = QLineEdit(settings.get("profile_path"))
        self.profile_name_input = QLineEdit(settings.get("profile_name"))
        self.extra_args_input = QLineEdit(settings.get("edge_extra_args"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(settings.get("theme") or "dark")

        edge_sec = QHBoxLayout()
        edge_sec.addWidget(self.edge_path_input)
        edge_browse = QPushButton("Gözat")
        edge_browse.clicked.connect(self._browse_edge)
        edge_sec.addWidget(edge_browse)

        profile_sec = QHBoxLayout()
        profile_sec.addWidget(self.profile_path_input)
        profile_browse = QPushButton("Gözat")
        profile_browse.clicked.connect(self._browse_profile)
        profile_sec.addWidget(profile_browse)

        form = QFormLayout()
        form.addRow("Edge exe yolu:", edge_sec)
        form.addRow("Edge profil klasörü:", profile_sec)
        form.addRow("Profil adı:", self.profile_name_input)
        form.addRow("Ek Edge parametreleri:", self.extra_args_input)
        form.addRow("Tema:", self.theme_combo)

        kaydet = QPushButton("Kaydet")
        iptal = QPushButton("İptal")
        kaydet.clicked.connect(self.accept)
        iptal.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(kaydet)
        buttons.addWidget(iptal)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def _browse_edge(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Edge EXE Seç", "", "Uygulama (*.exe)")
        if file_path:
            self.edge_path_input.setText(file_path)

    def _browse_profile(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Profil Klasörü Seç")
        if folder:
            self.profile_path_input.setText(folder)

    def values(self) -> dict:
        return {
            "edge_path": self.edge_path_input.text().strip(),
            "profile_path": self.profile_path_input.text().strip(),
            "profile_name": self.profile_name_input.text().strip() or "Default",
            "edge_extra_args": self.extra_args_input.text().strip(),
            "theme": self.theme_combo.currentText(),
        }


class MainWindow(QMainWindow):
    def __init__(self, db: MusicDatabase, settings: SettingsManager) -> None:
        super().__init__()
        self.db = db
        self.settings = settings
        self.current_record: Optional[MusicRecord] = None

        self.setWindowTitle("YouTube Müzik Yöneticisi")
        self.resize(1200, 720)
        self.setStatusBar(QStatusBar())

        self._build_ui()
        self._build_menu()
        self._apply_theme()
        self._load_records()

        if not self.settings.get("edge_path"):
            self.settings.set("edge_path", guess_edge_path())
            self.settings.set("profile_path", guess_edge_profile_path())
            self.settings.save()

    def _build_ui(self) -> None:
        central = QWidget()
        root_layout = QVBoxLayout(central)

        top_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Müzik adı, etiket veya not ara...")
        self.search_input.textChanged.connect(self._load_records)
        self.favorite_filter = QCheckBox("Sadece favoriler")
        self.favorite_filter.toggled.connect(self._load_records)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["İsme göre", "Son açılanlar"])
        self.sort_combo.currentTextChanged.connect(self._load_records)

        top_row.addWidget(QLabel("Arama:"))
        top_row.addWidget(self.search_input, 1)
        top_row.addWidget(self.favorite_filter)
        top_row.addWidget(QLabel("Sırala:"))
        top_row.addWidget(self.sort_combo)

        splitter = QSplitter(Qt.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._open_selected_in_edge)

        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        self.detail_baslik = QLabel("-")
        self.detail_url = QLabel("-")
        self.detail_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detail_tarih = QLabel("-")
        self.detail_son_acilis = QLabel("-")
        self.detail_etiketler = QLabel("-")
        self.detail_aciklama = QTextEdit()
        self.detail_aciklama.setReadOnly(False)
        self.detail_aciklama.setPlaceholderText("Seçili kaydın notunu burada düzenleyebilirsiniz...")

        info_box = QGroupBox("Kayıt Detayları")
        info_layout = QGridLayout(info_box)
        info_layout.addWidget(QLabel("Müzik Adı:"), 0, 0)
        info_layout.addWidget(self.detail_baslik, 0, 1)
        info_layout.addWidget(QLabel("URL:"), 1, 0)
        info_layout.addWidget(self.detail_url, 1, 1)
        info_layout.addWidget(QLabel("Eklenme:"), 2, 0)
        info_layout.addWidget(self.detail_tarih, 2, 1)
        info_layout.addWidget(QLabel("Son Açılış:"), 3, 0)
        info_layout.addWidget(self.detail_son_acilis, 3, 1)
        info_layout.addWidget(QLabel("Etiketler:"), 4, 0)
        info_layout.addWidget(self.detail_etiketler, 4, 1)

        details_layout.addWidget(info_box)
        details_layout.addWidget(QLabel("Açıklama / Not"))
        details_layout.addWidget(self.detail_aciklama, 1)

        splitter.addWidget(self.list_widget)
        splitter.addWidget(details_widget)
        splitter.setSizes([430, 770])

        bottom_buttons = QHBoxLayout()
        self.new_button = QPushButton("Yeni Ekle")
        self.edit_button = QPushButton("Düzenle")
        self.delete_button = QPushButton("Sil")
        self.open_button = QPushButton("Edge'de Aç ve Çal")
        self.copy_button = QPushButton("Link Kopyala")
        self.backup_button = QPushButton("Veritabanını Yedekle")
        self.save_note_button = QPushButton("Notu Kaydet")

        self.new_button.clicked.connect(self._new_record)
        self.edit_button.clicked.connect(self._edit_record)
        self.delete_button.clicked.connect(self._delete_record)
        self.open_button.clicked.connect(self._open_selected_in_edge)
        self.copy_button.clicked.connect(self._copy_link)
        self.backup_button.clicked.connect(self._backup_database)
        self.save_note_button.clicked.connect(self._save_note)

        for btn in [
            self.new_button,
            self.edit_button,
            self.delete_button,
            self.open_button,
            self.copy_button,
            self.save_note_button,
            self.backup_button,
        ]:
            bottom_buttons.addWidget(btn)

        root_layout.addLayout(top_row)
        root_layout.addWidget(splitter, 1)
        root_layout.addLayout(bottom_buttons)

        self.setCentralWidget(central)

    def _build_menu(self) -> None:
        toolbar = QToolBar("Araçlar")
        self.addToolBar(toolbar)

        ayarlar_action = QAction("Ayarlar", self)
        ayarlar_action.triggered.connect(self._open_settings)
        toolbar.addAction(ayarlar_action)

        disa_json_action = QAction("JSON Dışa Aktar", self)
        disa_json_action.triggered.connect(lambda: self._export_data("json"))
        toolbar.addAction(disa_json_action)

        ice_json_action = QAction("JSON İçe Aktar", self)
        ice_json_action.triggered.connect(lambda: self._import_data("json"))
        toolbar.addAction(ice_json_action)

        disa_csv_action = QAction("CSV Dışa Aktar", self)
        disa_csv_action.triggered.connect(lambda: self._export_data("csv"))
        toolbar.addAction(disa_csv_action)

        ice_csv_action = QAction("CSV İçe Aktar", self)
        ice_csv_action.triggered.connect(lambda: self._import_data("csv"))
        toolbar.addAction(ice_csv_action)

    def _apply_theme(self) -> None:
        dark_style = """
            QWidget { background-color: #1f2933; color: #e5e7eb; font-size: 13px; }
            QLineEdit, QTextEdit, QListWidget, QComboBox { background-color: #111827; border: 1px solid #374151; border-radius: 6px; padding: 6px; }
            QPushButton { background-color: #2563eb; border: none; border-radius: 6px; padding: 8px 12px; color: white; }
            QPushButton:hover { background-color: #1d4ed8; }
            QToolBar { border: none; spacing: 8px; }
            QGroupBox { border: 1px solid #374151; border-radius: 8px; margin-top: 10px; padding-top: 10px; }
        """
        light_style = """
            QWidget { background-color: #f3f4f6; color: #111827; font-size: 13px; }
            QLineEdit, QTextEdit, QListWidget, QComboBox { background-color: white; border: 1px solid #d1d5db; border-radius: 6px; padding: 6px; }
            QPushButton { background-color: #2563eb; border: none; border-radius: 6px; padding: 8px 12px; color: white; }
            QPushButton:hover { background-color: #1d4ed8; }
            QToolBar { border: none; spacing: 8px; }
            QGroupBox { border: 1px solid #d1d5db; border-radius: 8px; margin-top: 10px; padding-top: 10px; }
        """
        QApplication.instance().setStyleSheet(dark_style if self.settings.get("theme") == "dark" else light_style)

    def _validate_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and "youtube" in parsed.netloc.lower()

    def _load_records(self) -> None:
        query = self.search_input.text().strip()
        only_fav = self.favorite_filter.isChecked()
        sort = "son_acilan" if self.sort_combo.currentText() == "Son açılanlar" else "baslik"

        self.list_widget.clear()
        records = self.db.search_records(query=query, only_favorites=only_fav, sort_by=sort)

        for record in records:
            label = f"{'★ ' if record.favori_mi else ''}{record.baslik}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, record.id)
            self.list_widget.addItem(item)

        self.statusBar().showMessage(f"Toplam {len(records)} kayıt listelendi.")

    def _selected_record(self) -> Optional[MusicRecord]:
        item = self.list_widget.currentItem()
        if not item:
            return None
        record_id = item.data(Qt.UserRole)
        return self.db.get_record(record_id)

    def _on_selection_changed(self) -> None:
        self.current_record = self._selected_record()
        if not self.current_record:
            self._clear_detail()
            return

        rec = self.current_record
        self.detail_baslik.setText(rec.baslik)
        self.detail_url.setText(rec.url)
        self.detail_tarih.setText(rec.eklenme_tarihi)
        self.detail_son_acilis.setText(rec.son_acilis_tarihi or "Henüz açılmadı")
        self.detail_etiketler.setText(rec.etiketler or "-")
        self.detail_aciklama.setPlainText(rec.aciklama)

    def _clear_detail(self) -> None:
        self.detail_baslik.setText("-")
        self.detail_url.setText("-")
        self.detail_tarih.setText("-")
        self.detail_son_acilis.setText("-")
        self.detail_etiketler.setText("-")
        self.detail_aciklama.setPlainText("")

    def _new_record(self) -> None:
        dialog = MusicDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        values = dialog.values()
        if not values["baslik"] or not values["url"]:
            QMessageBox.warning(self, "Eksik Bilgi", "Müzik adı ve YouTube linki zorunludur.")
            return

        if not self._validate_url(values["url"]):
            QMessageBox.warning(self, "Geçersiz Link", "Lütfen geçerli bir YouTube linki girin.")
            return

        record = MusicRecord(
            id=None,
            baslik=values["baslik"],
            url=values["url"],
            aciklama=values["aciklama"],
            favori_mi=values["favori_mi"],
            eklenme_tarihi=datetime.now().isoformat(timespec="seconds"),
            son_acilis_tarihi=None,
            etiketler=values["etiketler"],
        )

        try:
            self.db.add_record(record)
            self._load_records()
            self.statusBar().showMessage("Yeni kayıt eklendi.", 4000)
        except DatabaseError as exc:
            QMessageBox.warning(self, "Kayıt Hatası", str(exc))

    def _edit_record(self) -> None:
        record = self._selected_record()
        if not record:
            QMessageBox.information(self, "Kayıt Seçin", "Lütfen düzenlemek için bir kayıt seçin.")
            return

        dialog = MusicDialog(self, record)
        if dialog.exec() != QDialog.Accepted:
            return

        values = dialog.values()
        if not values["baslik"] or not values["url"]:
            QMessageBox.warning(self, "Eksik Bilgi", "Müzik adı ve YouTube linki zorunludur.")
            return

        if not self._validate_url(values["url"]):
            QMessageBox.warning(self, "Geçersiz Link", "Lütfen geçerli bir YouTube linki girin.")
            return

        updated = MusicRecord(
            id=record.id,
            baslik=values["baslik"],
            url=values["url"],
            aciklama=values["aciklama"],
            favori_mi=values["favori_mi"],
            eklenme_tarihi=record.eklenme_tarihi,
            son_acilis_tarihi=record.son_acilis_tarihi,
            etiketler=values["etiketler"],
        )

        try:
            self.db.update_record(updated)
            self._load_records()
            self.statusBar().showMessage("Kayıt güncellendi.", 4000)
        except DatabaseError as exc:
            QMessageBox.warning(self, "Güncelleme Hatası", str(exc))

    def _delete_record(self) -> None:
        record = self._selected_record()
        if not record:
            QMessageBox.information(self, "Kayıt Seçin", "Silmek için bir kayıt seçin.")
            return

        result = QMessageBox.question(
            self,
            "Silme Onayı",
            f"'{record.baslik}' kaydı silinsin mi?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if result == QMessageBox.Yes and record.id is not None:
            self.db.delete_record(record.id)
            self._load_records()
            self._clear_detail()
            self.statusBar().showMessage("Kayıt silindi.", 4000)

    def _save_note(self) -> None:
        record = self._selected_record()
        if not record:
            QMessageBox.information(self, "Kayıt Seçin", "Önce bir kayıt seçin.")
            return
        record.aciklama = self.detail_aciklama.toPlainText().strip()
        try:
            self.db.update_record(record)
            self.statusBar().showMessage("Not kaydedildi.", 3000)
        except DatabaseError as exc:
            QMessageBox.warning(self, "Hata", str(exc))

    def _copy_link(self) -> None:
        record = self._selected_record()
        if not record:
            QMessageBox.information(self, "Kayıt Seçin", "Önce bir kayıt seçin.")
            return
        QApplication.clipboard().setText(record.url)
        self.statusBar().showMessage("Link panoya kopyalandı.", 3000)

    def _open_selected_in_edge(self) -> None:
        record = self._selected_record()
        if not record or record.id is None:
            QMessageBox.information(self, "Kayıt Seçin", "Önce bir kayıt seçin.")
            return

        try:
            open_url_in_edge(
                url=record.url,
                edge_path=self.settings.get("edge_path"),
                profile_path=self.settings.get("profile_path"),
                profile_name=self.settings.get("profile_name") or "Default",
                extra_args=self.settings.get("edge_extra_args"),
            )
            self.db.mark_opened_now(record.id)
            self._load_records()
            self.statusBar().showMessage("Bağlantı Edge üzerinde açıldı.", 4000)
        except EdgeLaunchError as exc:
            QMessageBox.critical(self, "Edge Hatası", str(exc))

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() != QDialog.Accepted:
            return

        values = dialog.values()
        for key, value in values.items():
            self.settings.set(key, value)
        self.settings.save()
        self._apply_theme()
        self.statusBar().showMessage("Ayarlar kaydedildi.", 4000)

    def _export_data(self, fmt: str) -> None:
        records = self.db.search_records()
        try:
            if fmt == "json":
                file_path, _ = QFileDialog.getSaveFileName(self, "JSON Dışa Aktar", "muzikler.json", "JSON (*.json)")
                if file_path:
                    self.db.export_json(Path(file_path), records)
            else:
                file_path, _ = QFileDialog.getSaveFileName(self, "CSV Dışa Aktar", "muzikler.csv", "CSV (*.csv)")
                if file_path:
                    self.db.export_csv(Path(file_path), records)
            self.statusBar().showMessage(f"{fmt.upper()} dışa aktarma tamamlandı.", 4000)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Dışa Aktarma Hatası", f"İşlem başarısız: {exc}")

    def _import_data(self, fmt: str) -> None:
        try:
            if fmt == "json":
                file_path, _ = QFileDialog.getOpenFileName(self, "JSON İçe Aktar", "", "JSON (*.json)")
                if not file_path:
                    return
                count = self.db.import_json(Path(file_path))
            else:
                file_path, _ = QFileDialog.getOpenFileName(self, "CSV İçe Aktar", "", "CSV (*.csv)")
                if not file_path:
                    return
                count = self.db.import_csv(Path(file_path))

            self._load_records()
            QMessageBox.information(self, "İçe Aktarma", f"{count} kayıt içe aktarıldı.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "İçe Aktarma Hatası", f"İşlem başarısız: {exc}")

    def _backup_database(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Veritabanı Yedeği", "muzik_yedek.db", "SQLite (*.db)")
        if not file_path:
            return
        try:
            self.db.backup_database(Path(file_path))
            self.statusBar().showMessage("Veritabanı yedeği alındı.", 4000)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Yedekleme Hatası", f"Yedekleme başarısız: {exc}")
