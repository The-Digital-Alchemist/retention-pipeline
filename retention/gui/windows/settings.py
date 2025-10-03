from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QCheckBox,
    QButtonGroup,
    QLineEdit,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from ..utils.styles import settings_dialog_styles


class SettingsDialog(QDialog):
    settings_changed = Signal(dict)

    def __init__(self, parent=None, current_api_key=""):
        super().__init__(parent)
        self.current_api_key = current_api_key
        self.setWindowTitle("Settings")
        self.setFixedSize(360, 280)
        self.setModal(True)
        self.setStyleSheet(settings_dialog_styles())
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("Retention preferences")
        header.setObjectName("dialogTitle")

        subheader = QLabel("Keep your API key handy and decide how flashcards behave.")
        subheader.setObjectName("dialogSubtitle")
        subheader.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(subheader)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setMinimumHeight(42)
        self.api_key_input.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.api_key_input.setText(self.current_api_key)
        self.api_key_input.setObjectName("apiKeyInput")

        trust_label = QLabel("Stored locally on this machine")
        trust_label.setObjectName("hintLabel")

        layout.addWidget(self.api_key_input)
        layout.addWidget(trust_label)

        toggle_row = QHBoxLayout()
        toggle_row.setContentsMargins(0, 0, 0, 0)
        toggle_row.setSpacing(12)

        toggle_label = QLabel("Flashcards")
        toggle_label.setObjectName("sectionLabel")

        self.flashcards_toggle = QCheckBox()
        self.flashcards_toggle.setChecked(True)
        self.flashcards_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.flashcards_toggle.setObjectName("toggleSwitch")
        self.flashcards_toggle.toggled.connect(self._on_flashcards_toggled)

        toggle_row.addWidget(toggle_label)
        toggle_row.addStretch()
        toggle_row.addWidget(self.flashcards_toggle)

        layout.addLayout(toggle_row)

        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(0, 0, 0, 0)
        mode_row.setSpacing(8)

        self.mode_group = QButtonGroup()

        self.quick_btn = QPushButton("Quick")
        self.quick_btn.setCheckable(True)
        self.quick_btn.setChecked(True)
        self.quick_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quick_btn.setMinimumHeight(32)
        self.quick_btn.setObjectName("modeButton")

        self.deep_btn = QPushButton("Deep")
        self.deep_btn.setCheckable(True)
        self.deep_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.deep_btn.setMinimumHeight(32)
        self.deep_btn.setObjectName("modeButton")

        self.mode_group.addButton(self.quick_btn, 0)
        self.mode_group.addButton(self.deep_btn, 1)

        mode_row.addWidget(self.quick_btn)
        mode_row.addWidget(self.deep_btn)
        mode_row.addStretch()

        layout.addLayout(mode_row)
        layout.addStretch()

        self.done_btn = QPushButton("Save")
        self.done_btn.setMinimumHeight(38)
        self.done_btn.setDefault(True)
        self.done_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.done_btn.clicked.connect(self._on_done)
        self.done_btn.setObjectName("primaryButton")

        layout.addWidget(self.done_btn)

    def _on_flashcards_toggled(self, checked):
        for button in (self.quick_btn, self.deep_btn):
            button.setVisible(checked)

    def _on_done(self):
        settings = {
            "api_key": self.api_key_input.text().strip(),
            "flashcards": {
                "enabled": self.flashcards_toggle.isChecked(),
                "mode": "quick" if self.quick_btn.isChecked() else "deep",
            },
        }
        self.settings_changed.emit(settings)
        self.accept()

    def get_settings(self):
        return {
            "api_key": self.api_key_input.text().strip(),
            "flashcards": {
                "enabled": self.flashcards_toggle.isChecked(),
                "mode": "quick" if self.quick_btn.isChecked() else "deep",
            },
        }

    def set_settings(self, settings):
        if "api_key" in settings:
            self.api_key_input.setText(settings["api_key"])

        if "flashcards" in settings:
            flashcard_settings = settings["flashcards"]
            if "enabled" in flashcard_settings:
                self.flashcards_toggle.setChecked(flashcard_settings["enabled"])
            if "mode" in flashcard_settings:
                if flashcard_settings["mode"] == "quick":
                    self.quick_btn.setChecked(True)
                else:
                    self.deep_btn.setChecked(True)

