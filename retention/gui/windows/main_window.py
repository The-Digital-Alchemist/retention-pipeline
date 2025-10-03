from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QApplication,
    QMessageBox,
    QLabel,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QStyle,
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QMouseEvent, QShortcut, QKeySequence, QCursor, QColor
from pathlib import Path
from datetime import datetime
import whisper

from .settings import SettingsDialog
from ...recording.SysAudio import AudioRecorder
from ...nlp.chunk import chunk_file
from ...nlp.summarize import summarize_file
from ...nlp.flashcards import deep_flashcard, quick_flashcard
from ..components.validation_display import ValidationDisplay
from ..utils.styles import main_window_styles


class MainWindow(QWidget):
    record_requested = Signal()
    stop_requested = Signal()
    settings_changed = Signal(dict)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.is_recording = False
        self.is_processing = False
        self.flashcard_settings = {"enabled": True, "mode": "quick"}
        self.current_audio_file = None

        self.audio_recorder = AudioRecorder()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_position = QPoint()

        self._setup_ui()
        self._check_initial_state()

    def _setup_ui(self):
        self.setFixedWidth(320)
        self.setStyleSheet(main_window_styles())

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("surface")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(15, 23, 42, 50))
        shadow.setOffset(0, 6)
        surface.setGraphicsEffect(shadow)

        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(16, 16, 16, 16)
        surface_layout.setSpacing(12)

        root_layout.addWidget(surface)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)

        title_stack = QVBoxLayout()
        title_stack.setContentsMargins(0, 0, 0, 0)
        title_stack.setSpacing(2)

        title_label = QLabel("Summit")
        title_label.setObjectName("appTitle")

        subtitle_label = QLabel("AI Learning Accelerator")
        subtitle_label.setObjectName("appSubtitle")

        title_stack.addWidget(title_label)
        title_stack.addWidget(subtitle_label)

        header_row.addLayout(title_stack)
        header_row.addStretch()

        style = QApplication.style()

        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("iconButton")
        self.settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.settings_btn.setIconSize(QSize(16, 16))
        self.settings_btn.clicked.connect(self._on_settings_clicked)

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("iconButton")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setToolTip("Close (Esc)")
        self.close_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        self.close_btn.setIconSize(QSize(14, 14))
        self.close_btn.clicked.connect(self._on_close_clicked)

        header_row.addWidget(self.settings_btn)
        header_row.addWidget(self.close_btn)

        surface_layout.addLayout(header_row)

        chip_row = QHBoxLayout()
        chip_row.setContentsMargins(0, 0, 0, 0)
        chip_row.setSpacing(6)

        self.status_chip = QLabel("Ready")
        self.status_chip.setObjectName("statusChip")
        self.status_chip.setProperty("state", "idle")

        self.api_badge = QLabel()
        self.api_badge.setObjectName("chip")

        self.flashcard_badge = QLabel()
        self.flashcard_badge.setObjectName("chip")

        chip_row.addWidget(self.status_chip)
        chip_row.addStretch()
        chip_row.addWidget(self.api_badge)
        chip_row.addWidget(self.flashcard_badge)

        surface_layout.addLayout(chip_row)

        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(0, 0, 0, 0)
        controls_row.setSpacing(8)

        self.record_btn = QPushButton("Record")
        self.record_btn.setObjectName("primaryButton")
        self.record_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.record_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.record_btn.setMinimumHeight(44)
        self.record_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.record_btn.setIconSize(QSize(18, 18))
        self.record_btn.setToolTip("Start recording (Space)")
        self.record_btn.clicked.connect(self._on_record_clicked)

        self.stop_btn = QPushButton("Process")
        self.stop_btn.setObjectName("secondaryButton")
        self.stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.stop_btn.setMinimumHeight(44)
        self.stop_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.setIconSize(QSize(18, 18))
        self.stop_btn.setToolTip("Stop and process (Space)")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_clicked)

        controls_row.addWidget(self.record_btn)
        controls_row.addWidget(self.stop_btn)

        surface_layout.addLayout(controls_row)

        self.status_label = QLabel("Ready to capture.")
        self.status_label.setObjectName("statusHeadline")
        self.status_label.setWordWrap(True)

        self.status_detail = QLabel("Press Record to capture system audio.")
        self.status_detail.setObjectName("statusDetail")
        self.status_detail.setWordWrap(True)

        surface_layout.addWidget(self.status_label)
        surface_layout.addWidget(self.status_detail)

        self.helper_label = QLabel("")
        self.helper_label.setObjectName("helperText")
        self.helper_label.setWordWrap(True)
        self.helper_label.setVisible(False)

        surface_layout.addWidget(self.helper_label)

        self.output_label = QLabel()
        self.output_label.setObjectName("outputHint")
        self.output_label.setWordWrap(True)
        self.output_label.setVisible(False)

        surface_layout.addWidget(self.output_label)

        self.validation_display = ValidationDisplay()
        self.validation_display.setObjectName("validationDisplay")
        self.validation_display.setVisible(False)
        self.validation_display.validation_failed.connect(self._on_validation_failed)
        self.validation_display.validation_passed.connect(self._on_validation_passed)

        surface_layout.addWidget(self.validation_display)

        self._setup_shortcuts()
        self._update_flashcard_badge()
        self._update_api_badge()
        self._set_status("Ready to capture.", state="idle")

    def _setup_shortcuts(self):
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self._on_close_clicked)

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self._on_close_clicked)

        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self._toggle_record)

    def _refresh_chip(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _show_helper_message(self, message: str) -> None:
        self.helper_label.setText(message)
        self.helper_label.setVisible(True)

    def _set_status(self, message, state="idle", detail=None):
        state_labels = {
            "idle": "Ready",
            "recording": "Recording",
            "processing": "Working",
            "success": "Done",
            "warning": "Check",
            "error": "Error",
            "info": "Info",
        }
        self.status_chip.setText(state_labels.get(state, state.title()))
        self.status_chip.setProperty("state", state)
        self._refresh_chip(self.status_chip)

        self.status_label.setText(message)
        if detail is not None:
            self.status_detail.setText(detail)

    def _update_flashcard_badge(self):
        enabled = self.flashcard_settings.get("enabled", True)
        mode = self.flashcard_settings.get("mode", "quick").capitalize()
        if enabled:
            self.flashcard_badge.setText(f"Flashcards | {mode}")
            badge_state = "accent" if mode.lower() == "deep" else "info"
        else:
            self.flashcard_badge.setText("Flashcards | Off")
            badge_state = "muted"
        self.flashcard_badge.setProperty("state", badge_state)
        self._refresh_chip(self.flashcard_badge)

    def _update_api_badge(self):
        if self._is_api_key_valid():
            self.api_badge.setText("API key linked")
            badge_state = "success"
        else:
            self.api_badge.setText("API key needed")
            badge_state = "warning"
        self.api_badge.setProperty("state", badge_state)
        self._refresh_chip(self.api_badge)

    def _style_message_box(self, box, accent="#2563eb"):
        box.setStyleSheet(
            (
                "QMessageBox {\n"
                "    background-color: #ffffff;\n"
                "    color: #2d3748;\n"
                "    font-family: 'Segoe UI', Arial, sans-serif;\n"
                "}\n"
                "QMessageBox QLabel {\n"
                "    color: #2d3748;\n"
                "    background-color: transparent;\n"
                "    font-size: 14px;\n"
                "    padding: 10px;\n"
                "}\n"
                "QMessageBox QPushButton {\n"
                f"    background-color: {accent};\n"
                "    color: white;\n"
                "    border: none;\n"
                "    border-radius: 6px;\n"
                "    padding: 8px 16px;\n"
                "    font-size: 14px;\n"
                "    font-weight: bold;\n"
                "    min-width: 80px;\n"
                "    min-height: 32px;\n"
                "}\n"
                "QMessageBox QPushButton:hover {\n"
                "    background-color: #1d4ed8;\n"
                "    cursor: pointinghand;\n"
                "}\n"
                "QMessageBox QPushButton:pressed {\n"
                "    background-color: #1e3a8a;\n"
                "}\n"
            )
        )

    def _toggle_record(self):
        if self.is_recording:
            self._on_stop_clicked()
        else:
            self._on_record_clicked()

    def _on_record_clicked(self):
        if not self._is_api_key_valid():
            self._set_status(
                "Add your OpenAI API key to get started.",
                state="warning",
                detail="Open Settings and paste your key before recording.",
            )
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("API Key Required")
            msg_box.setText("Please add your OpenAI API key in Settings before recording.")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            self._style_message_box(msg_box, accent="#f97316")
            msg_box.exec()
            return

        self.is_recording = True
        self.is_processing = False
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.stop_btn.setFocus()
        self._set_status(
            "Recording",
            state="recording",
            detail="Press Process when you are ready to wrap.",
        )
        self.record_requested.emit()

    def _on_stop_clicked(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.record_btn.setEnabled(True)
        self.record_btn.setFocus()
        self.stop_btn.setEnabled(False)
        self._set_status(
            "Processing",
            state="processing",
            detail="Saving audio and lining up transcription...",
        )
        self.stop_requested.emit()

    def _on_settings_clicked(self):
        dialog = SettingsDialog(self, self.api_key)
        dialog.set_settings({"api_key": self.api_key, "flashcards": self.flashcard_settings})

        if dialog.exec():
            settings = dialog.get_settings()
            self.api_key = settings["api_key"]
            self.flashcard_settings = settings["flashcards"]
            self.settings_changed.emit(settings)

            self._update_flashcard_badge()
            self._update_api_badge()

            self.validation_display._check_initial_validation()
            self._check_initial_state()

            if not self.is_recording and not self.is_processing:
                self._set_status(
                    "Settings updated",
                    state="info",
                    detail="Ready when you are.",
                )

    def load_settings(self, settings):
        from ...validation import sanitize_api_key

        self.api_key = sanitize_api_key(settings.get("api_key", ""))
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
        except Exception as exc:
            print(f"Recording error: {exc}")
            self.is_recording = False
            self.record_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self._set_status("Recording failed to start", state="error", detail=str(exc))

    def stop_recording(self):
        try:
            audio, sample_rate = self.audio_recorder.stop_recording()
            if audio is None:
                self._set_status(
                    "No audio captured",
                    state="warning",
                    detail="Try recording again; no audio samples were received.",
                )
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.data_dir / f"recording_{timestamp}.wav"
            self.audio_recorder.save_recording(str(output_path))
            print(f"Recording saved: {output_path}")
            self._show_helper_message(f"Recording saved: {output_path.name}")

            file_size = output_path.stat().st_size
            if file_size < 1024 * 1024:
                self._set_status(
                    "Recording too short",
                    state="warning",
                    detail="Capture at least 1MB of audio for accurate transcription.",
                )
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Recording Too Short")
                msg_box.setText("Recording is too short (less than 1MB). Please record for a longer duration.")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                self._style_message_box(msg_box, accent="#f97316")
                msg_box.exec()
                return

            self.current_audio_file = output_path
            self.validation_display.setVisible(True)
            self.validation_display.reset_file_validation()
            self.adjustSize()
            self.output_label.setVisible(False)

            if self.validation_display.validate_file(output_path):
                self.is_processing = True
                self._set_status(
                    "Processing",
                    state="processing",
                    detail="Transcribing, summarizing, and generating materials...",
                )
                self._run_pipeline(str(output_path), timestamp)
            else:
                self.is_processing = False
                self._set_status(
                    "Validation required",
                    state="warning",
                    detail="Resolve the validation issues shown below and try again.",
                )
                print("File validation failed, but keeping the recording")
        except Exception as exc:
            self.is_processing = False
            print(f"Stop recording error: {exc}")
            self._set_status("Stop recording failed", state="error", detail=str(exc))

    def _cleanup_intermediate_files(self, *paths: Path) -> None:
        for path in paths:
            if not path:
                continue
            try:
                if path.exists():
                    path.unlink()
            except Exception as exc:
                print(f"Cleanup warning for {path}: {exc}")

    def _run_pipeline(self, audio_path, timestamp):
        flashcard_path = None
        transcription_path = None
        chunk_file_path = None
        try:
            print("Starting pipeline...")

            model = whisper.load_model("base")

            print("Transcribing...")
            result = model.transcribe(audio_path)

            transcription_path = self.data_dir / "transcriptions" / f"recording_{timestamp}.txt"
            transcription_path.parent.mkdir(parents=True, exist_ok=True)
            transcription_path.write_text(result["text"], encoding="UTF-8")  # type: ignore
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

            self.validation_display.setVisible(False)
            self.adjustSize()

            outputs = [summaries_path.name]
            if flashcard_path is not None:
                outputs.append(flashcard_path.name)

            self._show_helper_message("Capture again when you are ready.")
            self.output_label.setText("Saved files: " + ", ".join(outputs))
            self.output_label.setVisible(True)
            self._set_status(
                "Complete",
                state="success",
                detail="Outputs are ready in the data folder.",
            )

            self._cleanup_intermediate_files(transcription_path, chunk_file_path)
        except Exception as exc:
            print(f"Pipeline error: {exc}")
            self._set_status(
                "Processing failed",
                state="error",
                detail="See the error details dialog for more information.",
            )
            self._show_pipeline_error(str(exc))
        finally:
            self.is_processing = False

    def get_api_key(self):
        return self.api_key

    def _on_validation_failed(self, error_msg):
        if not self.is_processing:
            self._set_status("Validation failed", state="warning", detail=error_msg)

        self.validation_display.setVisible(True)
        self.adjustSize()

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Validation Error")
        msg_box.setText("Validation failed")
        msg_box.setDetailedText(f"Error details: {error_msg}")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        self._style_message_box(msg_box, accent="#f97316")
        msg_box.exec()

    def _on_validation_passed(self):
        print("File validation passed")
        if not self.is_processing:
            self._set_status(
                "Validated",
                state="info",
                detail="Everything looks good.",
            )

    def validate_existing_file(self, file_path: Path):
        return self.validation_display.validate_file(file_path)

    def _check_initial_state(self):
        api_valid = self._is_api_key_valid()

        if not api_valid:
            self.record_btn.setEnabled(False)
            self.record_btn.setToolTip("Add your OpenAI API key in Settings to enable recording.")
            if not self.is_recording and not self.is_processing:
                self._set_status(
                    "Add your OpenAI API key to get started.",
                    state="warning",
                    detail="Open Settings and paste your key before recording.",
                )
        else:
            self.record_btn.setEnabled(True)
            self.record_btn.setToolTip("Start recording (Space)")

        self._update_api_badge()

    def _is_api_key_valid(self):
        from ...validation import validate_api_key

        return validate_api_key()

    def _show_pipeline_error(self, error_msg):
        self.output_label.setVisible(False)
        self._show_helper_message("We hit a snag. Try again when you are ready.")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Pipeline Error")
        msg_box.setText("Something went wrong during processing. Please try again.")
        msg_box.setDetailedText(f"Error details: {error_msg}")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        self._style_message_box(msg_box, accent="#dc2626")
        msg_box.exec()


