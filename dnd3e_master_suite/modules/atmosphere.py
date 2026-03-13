from pathlib import Path

from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QSlider


class AtmospherePanel(QWidget):
    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.music = QMediaPlayer()
        self.ambience = QMediaPlayer()
        self.music_out = QAudioOutput()
        self.ambience_out = QAudioOutput()
        self.music.setAudioOutput(self.music_out)
        self.ambience.setAudioOutput(self.ambience_out)

        self.presets = self.data.read_json("data/presets/atmosphere_presets.json", [])
        preset_names = [p.get("name", "preset") for p in self.presets] or ["tavern", "dungeon", "battle"]

        self.preset_box = QComboBox()
        self.preset_box.addItems(preset_names)
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
        layout.addWidget(play)
        layout.addWidget(pause)
        layout.addWidget(stop)

        mv = QSlider()
        mv.setOrientation(Qt.Horizontal)
        mv.setRange(0, 100)
        mv.setValue(70)
        mv.valueChanged.connect(lambda v: self.music_out.setVolume(v / 100))

        av = QSlider()
        av.setOrientation(Qt.Horizontal)
        av.setRange(0, 100)
        av.setValue(55)
        av.valueChanged.connect(lambda v: self.ambience_out.setVolume(v / 100))

        layout.addWidget(QLabel("Music Volume"))
        layout.addWidget(mv)
        layout.addWidget(QLabel("Ambience Volume"))
        layout.addWidget(av)
        layout.addWidget(self.status)

    def activate_preset(self, name: str) -> None:
        preset = next((p for p in self.presets if p.get("name") == name), {})
        music_file = self.data.base_dir / "assets" / "music" / preset.get("music_file", f"{name}.mp3")
        ambience_file = self.data.base_dir / "assets" / "sounds" / preset.get("ambience_file", f"{name}.mp3")

        missing = []
        if Path(music_file).exists():
            self.music.setSource(QUrl.fromLocalFile(str(music_file)))
        else:
            missing.append(music_file.name)

        if Path(ambience_file).exists():
            self.ambience.setSource(QUrl.fromLocalFile(str(ambience_file)))
        else:
            missing.append(ambience_file.name)

        self.campaign.setdefault("atmosphere", {})["last_preset"] = name
        if missing:
            self.status.setText(f"Preset '{name}' loaded with missing files: {', '.join(missing)}")
        else:
            self.status.setText(f"Preset loaded: {name}")
