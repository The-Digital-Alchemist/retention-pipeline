from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QMessageBox
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent, QShortcut, QKeySequence, QCursor
from pathlib import Path
from datetime import datetime
import whisper
import json

from .settings import SettingsDialog
from ...recording.SysAudio import AudioRecorder
from ...nlp.chunk import chunk_file
from ...nlp.summarize import summarize_file
from ...nlp.flashcards import deep_flashcard, quick_flashcard
from ..components.validation_display import ValidationDisplay


class MainWindow(QWidget):
    record_requested = Signal()
    stop_requested = Signal()
    settings_changed = Signal(dict)
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.is_recording = False
        self.flashcard_settings = {"enabled": True, "mode": "quick"}
        self.current_audio_file = None
        
        self.audio_recorder = AudioRecorder(device_id=14, channels=1)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_position = QPoint()
        
        self._setup_ui()
        self._check_initial_state()
    
    def _setup_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(8, 8, 8, 8)
        self.setStyleSheet(self._get_stylesheet())
        
        # Button container
        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.record_btn = QPushButton("🎙️")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setFixedSize(50, 50)
        self.record_btn.setToolTip("Record")
        self.record_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.record_btn.clicked.connect(self._on_record_clicked)
        
        self.stop_btn = QPushButton("■")
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
        
        button_layout.addWidget(self.record_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.settings_btn)
        button_layout.addWidget(self.close_btn)
        
        # Validation display (initially hidden)
        self.validation_display = ValidationDisplay()
        self.validation_display.setObjectName("validationDisplay")
        self.validation_display.setVisible(False)
        self.validation_display.validation_failed.connect(self._on_validation_failed)
        self.validation_display.validation_passed.connect(self._on_validation_passed)
        
        # Add widgets to main layout
        main_layout.addWidget(button_container)
        main_layout.addWidget(self.validation_display)
        
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
        # Check if API key is valid before recording
        if not self._is_api_key_valid():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("API Key Required")
            msg_box.setText("Please add your OpenAI API key in Settings before recording.")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            
            # Apply custom styling
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                    color: #2d3748;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QMessageBox QLabel {
                    color: #2d3748;
                    background-color: transparent;
                    font-size: 14px;
                    padding: 10px;
                }
                QMessageBox QPushButton {
                    background-color: #ed8936;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 80px;
                    min-height: 32px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #dd6b20;
                    cursor: pointer;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #c05621;
                }
            """)
            
            msg_box.exec()
            return
            
        self.is_recording = True
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.record_requested.emit()
    
    def _on_stop_clicked(self):
        if not self.is_recording:
            return  # Prevent stopping when not recording
            
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
            
            # Re-check validation after API key change
            self.validation_display._check_initial_validation()
            self._check_initial_state()
    
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
        try:
            self.audio_recorder.start_recording()
        except Exception as e:
            print(f"Recording error: {e}")
    
    def stop_recording(self):
        try:
            audio, sample_rate = self.audio_recorder.stop_recording()
            if audio is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.data_dir / f"recording_{timestamp}.wav"
                self.audio_recorder.save_recording(str(output_path))
                print(f"Recording saved: {output_path}")
                
                # Check if recording is too short (less than 1MB)
                file_size = output_path.stat().st_size
                if file_size < 1024 * 1024:  # Less than 1MB
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Recording Too Short")
                    msg_box.setText("Recording is too short (less than 1MB). Please record for a longer duration.")
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    
                    # Apply custom styling
                    msg_box.setStyleSheet("""
                        QMessageBox {
                            background-color: #ffffff;
                            color: #2d3748;
                            font-family: 'Segoe UI', Arial, sans-serif;
                        }
                        QMessageBox QLabel {
                            color: #2d3748;
                            background-color: transparent;
                            font-size: 14px;
                            padding: 10px;
                        }
                        QMessageBox QPushButton {
                            background-color: #ed8936;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 8px 16px;
                            font-size: 14px;
                            font-weight: bold;
                            min-width: 80px;
                            min-height: 32px;
                        }
                        QMessageBox QPushButton:hover {
                            background-color: #dd6b20;
                            cursor: pointer;
                        }
                        QMessageBox QPushButton:pressed {
                            background-color: #c05621;
                        }
                    """)
                    
                    msg_box.exec()
                    return
                
                # Validate the recorded file before processing
                self.current_audio_file = output_path
                self.validation_display.setVisible(True)
                self.adjustSize()
                
                if self.validation_display.validate_file(output_path):
                    self._run_pipeline(str(output_path), timestamp)
                else:
                    # Validation failed, show error but keep the file
                    print("File validation failed, but keeping the recording")
        except Exception as e:
            print(f"Stop recording error: {e}")
    
    def _run_pipeline(self, audio_path, timestamp):
        try:
            print("Starting pipeline...")
            
            model = whisper.load_model("base")
            
            print("Transcribing...")
            result = model.transcribe(audio_path)
            
            transcription_path = self.data_dir / "transcriptions" / f"recording_{timestamp}.txt"
            transcription_path.parent.mkdir(parents=True, exist_ok=True)
            transcription_path.write_text(result["text"], encoding="UTF-8") # type: ignore
            print(f"Transcription saved: {transcription_path}")
            
            print("Chunking...")
            chunk_file(str(transcription_path))
            chunk_file_path = self.data_dir / "chunks" / f"recording_{timestamp}_chunks.json"
            print(f"Chunks saved: {chunk_file_path}")
            
            print("Summarizing...")
            summarize_file(str(chunk_file_path), api_key=self.api_key)
            summaries_path = self.data_dir / "summaries" / f"recording_{timestamp}_summaries.json"
            print(f"Summaries saved: {summaries_path}")
            
            if self.flashcard_settings.get("enabled", False):
                print("Generating flashcards...")
                flashcard_mode = self.flashcard_settings.get("mode", "quick")
                
                if flashcard_mode == "deep":
                    deep_flashcard(str(chunk_file_path), api_key=self.api_key)
                    flashcard_path = self.data_dir / "flashcards" / f"recording_{timestamp}_chunks_flashcards.md"
                else:
                    quick_flashcard(str(summaries_path), api_key=self.api_key)
                    flashcard_path = self.data_dir / "flashcards" / f"recording_{timestamp}_summaries_flashcards.md"
                
                print(f"Flashcards saved: {flashcard_path}")
            
            print("Pipeline completed successfully!")
            
            # Hide validation display after successful completion
            self.validation_display.setVisible(False)
            self.adjustSize()
            
        except Exception as e:
            print(f"Pipeline error: {e}")
            # Keep validation display visible on error
            self._show_pipeline_error(str(e))
    
    def get_api_key(self):
        return self.api_key
    
    def _on_validation_failed(self, error_msg):
        """Handle validation failure."""
        self.validation_display.setVisible(True)
        self.adjustSize()
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Validation Error")
        msg_box.setText("Validation failed")
        msg_box.setDetailedText(f"Error details: {error_msg}")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Apply custom styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2d3748;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox QLabel {
                color: #2d3748;
                background-color: transparent;
                font-size: 14px;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
                min-height: 32px;
            }
            QMessageBox QPushButton:hover {
                background-color: #dd6b20;
                cursor: pointer;
            }
            QMessageBox QPushButton:pressed {
                background-color: #c05621;
            }
        """)
        
        msg_box.exec()
    
    def _on_validation_passed(self):
        """Handle successful validation."""
        print("File validation passed")
    
    def validate_existing_file(self, file_path: Path):
        """Validate an existing file and show results."""
        return self.validation_display.validate_file(file_path)
    
    def _check_initial_state(self):
        """Check initial state and set button states accordingly."""
        # Check API key validity
        if not self._is_api_key_valid():
            self.record_btn.setEnabled(False)
            self.record_btn.setToolTip("Record (API key required)")
        else:
            self.record_btn.setEnabled(True)
            self.record_btn.setToolTip("Record")
    
    def _is_api_key_valid(self):
        """Check if API key is valid."""
        from ...validation import validate_api_key
        return validate_api_key()
    
    def _show_pipeline_error(self, error_msg):
        """Show pipeline error modal."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Pipeline Error")
        msg_box.setText("Something went wrong during processing. Please try again.")
        msg_box.setDetailedText(f"Error details: {error_msg}")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Apply custom styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2d3748;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox QLabel {
                color: #2d3748;
                background-color: transparent;
                font-size: 14px;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #e53e3e;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
                min-height: 32px;
            }
            QMessageBox QPushButton:hover {
                background-color: #c53030;
                cursor: pointer;
            }
            QMessageBox QPushButton:pressed {
                background-color: #9c2626;
            }
        """)
        
        msg_box.exec()
    
    def _get_stylesheet(self):
        return """
        QWidget {
            background-color: #ffffff;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
        }
        
        #buttonContainer {
            background: transparent;
            border: none;
        }
        
        #validationDisplay {
            background: transparent;
            border: none;
            border-top: 1px solid #e2e8f0;
            border-radius: 0px;
            margin-top: 8px;
            padding-top: 8px;
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
        
        #stopButton:!disabled {
            border-color: #e53e3e;
            background-color: #fff5f5;
        }
        
        #stopButton:hover:!disabled {
            background-color: #fed7d7;
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