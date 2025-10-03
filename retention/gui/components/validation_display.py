
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from pathlib import Path

from ...validation import validate_api_key, validate_file_type, validate_file_size
from ..utils.styles import validation_display_styles


class ValidationDisplay(QWidget):
    """A widget that displays validation status for API key and file validation."""

    validation_passed = Signal()
    validation_failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self._setup_ui()
        self._check_initial_validation()

    def _setup_ui(self):
        self.setObjectName("validationRoot")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.info_label = QLabel("We run a few quick checks before sending audio through the pipeline.")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.api_row, self.api_indicator, self.api_status = self._create_status_row("API key")
        layout.addWidget(self.api_row)

        self.file_row, self.file_indicator, self.file_status = self._create_status_row("File")
        self.file_row.setVisible(False)
        layout.addWidget(self.file_row)

        self.validate_btn = QPushButton("Re-run validation")
        self.validate_btn.setObjectName("validateButton")
        self.validate_btn.setFixedHeight(28)
        self.validate_btn.setEnabled(False)
        self.validate_btn.clicked.connect(self._validate_current_file)
        layout.addWidget(self.validate_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self._apply_styles()

    def _create_status_row(self, title):
        container = QWidget()
        container.setObjectName("statusRow")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        indicator = QLabel()
        indicator.setObjectName("statusIndicator")
        indicator.setFixedSize(10, 10)
        indicator.setProperty("state", "pending")

        title_label = QLabel(title)
        title_label.setObjectName("statusLabel")

        status_value = QLabel("Checking...")
        status_value.setObjectName("statusValue")

        row.addWidget(indicator)
        row.addWidget(title_label)
        row.addStretch()
        row.addWidget(status_value)

        return container, indicator, status_value

    def _apply_styles(self):
        self.setStyleSheet(validation_display_styles())


    def _set_indicator(self, indicator: QLabel, state: str):
        indicator.setProperty("state", state)
        indicator.style().unpolish(indicator)
        indicator.style().polish(indicator)

    def _check_initial_validation(self):
        if validate_api_key():
            self._set_indicator(self.api_indicator, "success")
            self.api_status.setText("Ready")
            self.api_status.setStyleSheet("color: #15803d;")
        else:
            self._set_indicator(self.api_indicator, "warning")
            self.api_status.setText("Add your key in Settings")
            self.api_status.setStyleSheet("color: #b45309;")

    def validate_file(self, file_path: Path):
        self.current_file = file_path
        self.file_row.setVisible(True)
        self.file_status.setText("Checking...")
        self.file_status.setStyleSheet("color: #64748b;")
        self._set_indicator(self.file_indicator, "pending")

        if not validate_file_type(file_path):
            self._set_indicator(self.file_indicator, "error")
            message = "Invalid file type. Only audio files are allowed."
            self.file_status.setText(message)
            self.file_status.setStyleSheet("color: #dc2626;")
            self.validation_failed.emit(message)
            self.validate_btn.setEnabled(True)
            return False

        if not validate_file_size(file_path):
            self._set_indicator(self.file_indicator, "error")
            message = "Invalid file size. Must be between 1MB and 1GB."
            self.file_status.setText(message)
            self.file_status.setStyleSheet("color: #dc2626;")
            self.validation_failed.emit(message)
            self.validate_btn.setEnabled(True)
            return False

        self._set_indicator(self.file_indicator, "success")
        self.file_status.setText("Ready for processing")
        self.file_status.setStyleSheet("color: #15803d;")
        self.validate_btn.setEnabled(True)
        self.validation_passed.emit()
        return True

    def _validate_current_file(self):
        if self.current_file is not None:
            self.validate_file(self.current_file)

    def reset_file_validation(self):
        self.file_row.setVisible(False)
        self._set_indicator(self.file_indicator, "pending")
        self.file_status.setText("Checking...")
        self.file_status.setStyleSheet("color: #64748b;")
        self.validate_btn.setEnabled(False)

    def get_validation_status(self):
        return validate_api_key()
