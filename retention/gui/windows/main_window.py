"""
Frameless minimal toolbar - Loom-style
Just 3 buttons: Record, Stop, Settings
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QToolButton, QApplication
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent, QShortcut, QKeySequence, QCursor

from .settings import SettingsDialog


class MainWindow(QWidget):
    """Frameless floating toolbar with just Record, Stop, Settings"""
    
    # Signals
    record_requested = Signal()
    stop_requested = Signal()
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.is_recording = False
        
        # Flashcard settings
        self.flashcard_settings = {
            "enabled": True,
            "mode": "quick"
        }
        
        # Make frameless
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # For dragging
        self._drag_position = QPoint()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup minimal 3-button toolbar"""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Container for rounded background
        self.setStyleSheet(self._get_stylesheet())
        
        # Record button
        self.record_btn = QPushButton("🎙️")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setFixedSize(50, 50)
        self.record_btn.setToolTip("Record")
        self.record_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.record_btn.clicked.connect(self._on_record_clicked)
        
        # Stop button
        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setFixedSize(50, 50)
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("settingsButton")
        self.settings_btn.setFixedSize(50, 50)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setToolTip("Close (Esc)")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.clicked.connect(self._on_close_clicked)
        
        # Add buttons
        layout.addWidget(self.record_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.close_btn)
        
        # Size to fit buttons
        self.adjustSize()
        
        # Add keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # ESC to close
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self._on_close_clicked)
        
        # Ctrl+Q to quit
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self._on_close_clicked)
        
        # Space to record/stop
        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self._toggle_record)
    
    def _toggle_record(self):
        """Toggle between record and stop"""
        if self.is_recording:
            self._on_stop_clicked()
        else:
            self._on_record_clicked()
    
    def _on_record_clicked(self):
        """Handle record button click"""
        self.is_recording = True
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.record_requested.emit()
        print("🎙️ Recording started...")
    
    def _on_stop_clicked(self):
        """Handle stop button click"""
        self.is_recording = False
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_requested.emit()
        print("⏹️ Recording stopped")
    
    def _on_settings_clicked(self):
        """Handle settings button click"""
        dialog = SettingsDialog(self, self.api_key)
        dialog.set_settings({
            "api_key": self.api_key,
            "flashcards": self.flashcard_settings
        })
        
        if dialog.exec():
            settings = dialog.get_settings()
            self.api_key = settings["api_key"]
            self.flashcard_settings = settings["flashcards"]
            print(f"⚙️ Settings updated: API key changed, Flashcards: {self.flashcard_settings}")
    
    def _on_close_clicked(self):
        """Handle close button click - properly quit the application"""
        print("👋 Closing Retention Pipeline...")
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event - ensure app quits"""
        print("👋 Closing Retention Pipeline...")
        QApplication.quit()
        event.accept()
    
    # Make toolbar draggable
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    # Stub functions for pipeline integration
    def start_recording(self):
        """
        TODO: Integrate with retention.recording.SysAudio
        Start recording audio
        """
        print("🎙️ Starting recording...")
        # TODO: Add your recording logic here
        pass
    
    def stop_recording(self):
        """
        TODO: Stop recording and save to data/transcriptions/
        """
        print("⏹️ Stopping recording...")
        # TODO: Add your stop recording logic here
        pass
    
    def get_api_key(self):
        """Get the current API key"""
        return self.api_key
    
    def _get_stylesheet(self):
        """Ultra-minimal Loom-style stylesheet"""
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
