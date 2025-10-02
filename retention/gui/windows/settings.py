from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QButtonGroup, QLineEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor


class SettingsDialog(QDialog):
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None, current_api_key=""):
        super().__init__(parent)
        self.current_api_key = current_api_key
        self.setWindowTitle("Settings")
        self.setFixedSize(420, 320)
        self.setModal(True)
        self.setStyleSheet(self._get_stylesheet())
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(35, 35, 35, 35)
        
        api_label = QLabel("API Key")
        api_label.setStyleSheet("color: #2d3748; font-size: 13px; font-weight: 600; margin-bottom: 4px;")
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setMinimumHeight(44)
        self.api_key_input.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.api_key_input.setText(self.current_api_key)
        self.api_key_input.setObjectName("apiKeyInput")
        
        trust_label = QLabel("Stored locally, never shared")
        trust_label.setStyleSheet("color: #a0aec0; font-size: 11px; margin-top: 2px;")
        
        toggle_container = QHBoxLayout()
        toggle_container.setSpacing(12)
        
        toggle_label = QLabel("Flashcards")
        toggle_label.setStyleSheet("color: #4a5568; font-size: 13px; font-weight: 500;")
        
        self.flashcards_toggle = QCheckBox()
        self.flashcards_toggle.setChecked(True)
        self.flashcards_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.flashcards_toggle.setObjectName("toggleSwitch")
        self.flashcards_toggle.toggled.connect(self._on_flashcards_toggled)
        
        toggle_container.addWidget(toggle_label)
        toggle_container.addWidget(self.flashcards_toggle)
        toggle_container.addStretch()
        
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(0)
        
        self.mode_group = QButtonGroup()
        
        self.quick_btn = QPushButton("Quick")
        self.quick_btn.setCheckable(True)
        self.quick_btn.setChecked(True)
        self.quick_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quick_btn.setMinimumHeight(32)
        self.quick_btn.setObjectName("modeButtonLeft")
        
        self.deep_btn = QPushButton("Deep")
        self.deep_btn.setCheckable(True)
        self.deep_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.deep_btn.setMinimumHeight(32)
        self.deep_btn.setObjectName("modeButtonRight")
        
        self.mode_group.addButton(self.quick_btn, 0)
        self.mode_group.addButton(self.deep_btn, 1)
        
        mode_layout.addWidget(self.quick_btn)
        mode_layout.addWidget(self.deep_btn)
        mode_layout.addStretch()
        
        self.done_btn = QPushButton("Done")
        self.done_btn.setMinimumHeight(32)
        self.done_btn.setMaximumHeight(32)
        self.done_btn.setDefault(True)
        self.done_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.done_btn.clicked.connect(self._on_done)
        self.done_btn.setObjectName("doneButton")
        
        layout.addWidget(api_label)
        layout.addWidget(self.api_key_input)
        layout.addWidget(trust_label)
        layout.addLayout(toggle_container)
        layout.addLayout(mode_layout)
        layout.addStretch()
        layout.addWidget(self.done_btn)
    
    def _on_flashcards_toggled(self, checked):
        for button in [self.quick_btn, self.deep_btn]:
            button.setVisible(checked)
    
    def _on_done(self):
        settings = {
            "api_key": self.api_key_input.text().strip(),
            "flashcards": {
                "enabled": self.flashcards_toggle.isChecked(),
                "mode": "quick" if self.quick_btn.isChecked() else "deep"
            }
        }
        self.settings_changed.emit(settings)
        self.accept()
    
    def get_settings(self):
        return {
            "api_key": self.api_key_input.text().strip(),
            "flashcards": {
                "enabled": self.flashcards_toggle.isChecked(),
                "mode": "quick" if self.quick_btn.isChecked() else "deep"
            }
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
    
    def _get_stylesheet(self):
        return """
        QDialog {
            background-color: #ffffff;
        }
        
        #apiKeyInput {
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 14px;
            background-color: #ffffff;
            color: #2d3748;
            font-family: monospace;
        }
        
        #apiKeyInput:focus {
            border-color: #3182ce;
        }
        
        #toggleSwitch {
            width: 28px;
            height: 16px;
        }
        
        #toggleSwitch::indicator {
            width: 28px;
            height: 16px;
            border-radius: 8px;
            background-color: #e2e8f0;
            border: none;
        }
        
        #toggleSwitch::indicator:checked {
            background-color: #3182ce;
            background-image: radial-gradient(circle, white 6px, transparent 6px);
            background-position: right 2px center;
            background-repeat: no-repeat;
        }
        
        #toggleSwitch::indicator:unchecked {
            background-color: #e2e8f0;
            background-image: radial-gradient(circle, white 6px, transparent 6px);
            background-position: left 2px center;
            background-repeat: no-repeat;
        }
        
        #modeButtonLeft, #modeButtonRight {
            background-color: #f7fafc;
            color: #4a5568;
            border: 2px solid #e2e8f0;
            font-size: 13px;
            font-weight: 500;
            padding: 6px 24px;
            min-width: 80px;
        }
        
        #modeButtonLeft {
            border-top-left-radius: 8px;
            border-bottom-left-radius: 8px;
            border-right: 1px solid #e2e8f0;
        }
        
        #modeButtonRight {
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            border-left: 1px solid #e2e8f0;
        }
        
        #modeButtonLeft:checked, #modeButtonRight:checked {
            background-color: #3182ce;
            color: white;
            border-color: #3182ce;
        }
        
        #modeButtonLeft:hover:!checked, #modeButtonRight:hover:!checked {
            background-color: #edf2f7;
        }
        
        #modeButtonLeft:checked:hover, #modeButtonRight:checked:hover {
            background-color: #2c5aa0;
        }
        
        #doneButton {
            background-color: #3182ce;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
        }
        
        #doneButton:hover {
            background-color: #2c5aa0;
        }
        
        QLabel {
            color: #4a5568;
        }
        """