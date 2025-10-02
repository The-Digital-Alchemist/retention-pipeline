from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from pathlib import Path
import os
from ...validation import validate_api_key, validate_file_type, validate_file_size


class ValidationDisplay(QWidget):
    """A widget that displays validation status for API key and file validation."""
    
    validation_passed = Signal()
    validation_failed = Signal(str)  # Error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._check_initial_validation()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # API Key validation
        self.api_key_container = QWidget()
        api_layout = QHBoxLayout(self.api_key_container)
        api_layout.setContentsMargins(0, 0, 0, 0)
        
        self.api_key_icon = QLabel("🔑")
        self.api_key_icon.setObjectName("apiKeyIcon")
        self.api_key_icon.setFixedSize(20, 20)
        
        self.api_key_label = QLabel("API Key")
        self.api_key_label.setObjectName("apiKeyLabel")
        font = QFont()
        font.setPointSize(9)
        self.api_key_label.setFont(font)
        
        self.api_key_status = QLabel("Checking...")
        self.api_key_status.setObjectName("apiKeyStatus")
        status_font = QFont()
        status_font.setPointSize(8)
        self.api_key_status.setFont(status_font)
        
        api_layout.addWidget(self.api_key_icon)
        api_layout.addWidget(self.api_key_label)
        api_layout.addStretch()
        api_layout.addWidget(self.api_key_status)
        
        # File validation (initially hidden)
        self.file_container = QWidget()
        self.file_container.setVisible(False)
        file_layout = QHBoxLayout(self.file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_icon = QLabel("📁")
        self.file_icon.setObjectName("fileIcon")
        self.file_icon.setFixedSize(20, 20)
        
        self.file_label = QLabel("File")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setFont(font)
        
        self.file_status = QLabel("")
        self.file_status.setObjectName("fileStatus")
        self.file_status.setFont(status_font)
        
        file_layout.addWidget(self.file_icon)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        file_layout.addWidget(self.file_status)
        
        # Validation button
        self.validate_btn = QPushButton("✓ Validate")
        self.validate_btn.setObjectName("validateButton")
        self.validate_btn.setFixedHeight(24)
        self.validate_btn.setEnabled(False)
        self.validate_btn.clicked.connect(self._validate_current_file)
        
        layout.addWidget(self.api_key_container)
        layout.addWidget(self.file_container)
        layout.addWidget(self.validate_btn)
        
        self._apply_styles()
    
    def _apply_styles(self):
        self.setStyleSheet("""
            #apiKeyLabel, #fileLabel {
                color: #2d3748;
                background: transparent;
            }
            
            #apiKeyStatus, #fileStatus {
                color: #718096;
                background: transparent;
            }
            
            #validateButton {
                background-color: #48bb78;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            
            #validateButton:hover {
                background-color: #38a169;
            }
            
            #validateButton:disabled {
                background-color: #a0aec0;
            }
        """)
    
    def _check_initial_validation(self):
        """Check API key validation on startup."""
        if validate_api_key():
            self.api_key_status.setText("✓ Valid")
            self.api_key_status.setStyleSheet("color: #48bb78;")
            self.api_key_icon.setText("🔑")
        else:
            self.api_key_status.setText("✗ Invalid")
            self.api_key_status.setStyleSheet("color: #e53e3e;")
            self.api_key_icon.setText("🔒")
            # Don't emit validation_failed signal on startup, just show status
    
    def validate_file(self, file_path: Path):
        """Validate a file and show the results."""
        self.file_container.setVisible(True)
        self.file_label.setText(f"File: {file_path.name}")
        
        # Check file type
        if not validate_file_type(file_path):
            self.file_status.setText("✗ Invalid type")
            self.file_status.setStyleSheet("color: #e53e3e;")
            self.file_icon.setText("❌")
            self.validation_failed.emit("Invalid file type. Only audio files are allowed.")
            return False
        
        # Check file size
        if not validate_file_size(file_path):
            self.file_status.setText("✗ Invalid size")
            self.file_status.setStyleSheet("color: #e53e3e;")
            self.file_icon.setText("❌")
            self.validation_failed.emit("Invalid file size. Must be between 1MB and 1GB.")
            return False
        
        # All validations passed
        self.file_status.setText("✓ Valid")
        self.file_status.setStyleSheet("color: #48bb78;")
        self.file_icon.setText("✅")
        self.validate_btn.setEnabled(True)
        self.validation_passed.emit()
        return True
    
    def _validate_current_file(self):
        """Re-validate the current file."""
        # This would be called if user wants to re-validate
        pass
    
    def reset_file_validation(self):
        """Reset file validation display."""
        self.file_container.setVisible(False)
        self.validate_btn.setEnabled(False)
        self.file_status.setText("")
        self.file_icon.setText("📁")
    
    def get_validation_status(self):
        """Get overall validation status."""
        api_valid = validate_api_key()
        return api_valid
