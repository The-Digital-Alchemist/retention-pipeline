from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent, QShortcut, QKeySequence, QCursor

from .settings import SettingsDialog


class MainWindow(QWidget):
    record_requested = Signal()
    stop_requested = Signal()
    settings_changed = Signal(dict)
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.is_recording = False
        self.flashcard_settings = {"enabled": True, "mode": "quick"}
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_position = QPoint()
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        self.setStyleSheet(self._get_stylesheet())
        
        self.record_btn = QPushButton("🎙️")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setFixedSize(50, 50)
        self.record_btn.setToolTip("Record")
        self.record_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.record_btn.clicked.connect(self._on_record_clicked)
        
        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setFixedSize(50, 50)
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("settingsButton")
        self.settings_btn.setFixedSize(50, 50)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setToolTip("Close (Esc)")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.clicked.connect(self._on_close_clicked)
        
        layout.addWidget(self.record_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.close_btn)
        
        self.adjustSize()
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self._on_close_clicked)
        
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self._on_close_clicked)
        
        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self._toggle_record)
    
    def _toggle_record(self):
        if self.is_recording:
            self._on_stop_clicked()
        else:
            self._on_record_clicked()
    
    def _on_record_clicked(self):
        self.is_recording = True
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.record_requested.emit()
    
    def _on_stop_clicked(self):
        self.is_recording = False
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_requested.emit()
    
    def _on_settings_clicked(self):
        dialog = SettingsDialog(self, self.api_key)
        dialog.set_settings({"api_key": self.api_key, "flashcards": self.flashcard_settings})
        
        if dialog.exec():
            settings = dialog.get_settings()
            self.api_key = settings["api_key"]
            self.flashcard_settings = settings["flashcards"]
            self.settings_changed.emit(settings)
    
    def load_settings(self, settings):
        self.api_key = settings.get("api_key", "")
        self.flashcard_settings = settings.get("flashcards", {"enabled": True, "mode": "quick"})
    
    def _on_close_clicked(self):
        QApplication.quit()
    
    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def start_recording(self):
        pass
    
    def stop_recording(self):
        pass
    
    def get_api_key(self):
        return self.api_key
    
    def _get_stylesheet(self):
        return """
        QWidget {
            background-color: #ffffff;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
        }
        
        QPushButton {
            background-color: #ffffff;
            color: #2d3748;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 24px;
        }
        
        QPushButton:hover {
            background-color: #f7fafc;
            border-color: #cbd5e0;
        }
        
        QPushButton:pressed {
            background-color: #edf2f7;
        }
        
        QPushButton:disabled {
            background-color: #f7fafc;
            opacity: 0.5;
        }
        
        #recordButton:!disabled {
            border-color: #e53e3e;
        }
        
        #recordButton:hover:!disabled {
            background-color: #fff5f5;
            border-color: #c53030;
        }
        
        #closeButton {
            background-color: #f7fafc;
            color: #a0aec0;
            border: 1px solid #e2e8f0;
            font-size: 16px;
            font-weight: bold;
        }
        
        #closeButton:hover {
            background-color: #fed7d7;
            color: #e53e3e;
            border-color: #feb2b2;
        }
        """