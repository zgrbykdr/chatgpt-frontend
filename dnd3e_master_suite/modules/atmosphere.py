from pathlib import Path
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QSlider, QMessageBox


class AtmospherePanel(QWidget):
    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.music = QMediaPlayer(); self.ambience = QMediaPlayer()
        self.music_out = QAudioOutput(); self.ambience_out = QAudioOutput()
        self.music.setAudioOutput(self.music_out); self.ambience.setAudioOutput(self.ambience_out)
        self.preset_box = QComboBox(); self.preset_box.addItems(["tavern", "dungeon", "forest", "battle", "horror"])
        self.status = QLabel("No preset active")
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self.preset_box)
        apply_btn = QPushButton("Apply Preset")
        apply_btn.clicked.connect(lambda: self.activate_preset(self.preset_box.currentText()))
        layout.addWidget(apply_btn)
        play = QPushButton("Play")
        play.clicked.connect(lambda: (self.music.play(), self.ambience.play()))
        pause = QPushButton("Pause")
        pause.clicked.connect(lambda: (self.music.pause(), self.ambience.pause()))
        stop = QPushButton("Stop")
        stop.clicked.connect(lambda: (self.music.stop(), self.ambience.stop()))
        layout.addWidget(play); layout.addWidget(pause); layout.addWidget(stop)
        mv = QSlider(); mv.setOrientation(Qt.Horizontal); mv.setRange(0, 100); mv.setValue(70); mv.valueChanged.connect(lambda v: self.music_out.setVolume(v / 100))
        av = QSlider(); av.setOrientation(Qt.Horizontal); av.setRange(0, 100); av.setValue(55); av.valueChanged.connect(lambda v: self.ambience_out.setVolume(v / 100))
        layout.addWidget(QLabel("Music Volume")); layout.addWidget(mv)
        layout.addWidget(QLabel("Ambience Volume")); layout.addWidget(av)
        layout.addWidget(self.status)

    def activate_preset(self, name: str) -> None:
        music_file = self.data.base_dir / "assets" / "music" / f"{name}.mp3"
        ambience_file = self.data.base_dir / "assets" / "sounds" / f"{name}.mp3"
        for fpath, player in [(music_file, self.music), (ambience_file, self.ambience)]:
            if Path(fpath).exists():
                player.setSource(QUrl.fromLocalFile(str(fpath)))
            else:
                QMessageBox.information(self, "Audio missing", f"Audio file not found: {fpath.name}. Running without it.")
        self.status.setText(f"Preset loaded: {name}")
