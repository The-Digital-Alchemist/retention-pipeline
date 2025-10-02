import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor


class APIKeySplash(QDialog):
    
    api_key_submitted = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Retention Pipeline")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self.setStyleSheet(self._get_stylesheet())
        
        self._center_on_screen()
        self.existing_key = self._load_from_env()
        self._setup_ui()
    
    def _center_on_screen(self):
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        
        title = QLabel("Retention Pipeline")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        
        subtitle = QLabel("AI-Powered Learning Assistant")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #718096; font-size: 16px; font-weight: 500;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        api_section = QVBoxLayout()
        api_section.setSpacing(15)
        
        api_label = QLabel("OpenAI API Key")
        api_label.setStyleSheet("color: #4a5568; font-size: 14px; font-weight: 600;")
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your OpenAI API key (sk-...)")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setMinimumHeight(50)
        self.api_key_input.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.api_key_input.returnPressed.connect(self._on_submit)
        self.api_key_input.setObjectName("apiKeyInput")
        
        help_text = QLabel("Your API key is stored locally and never shared")
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_text.setStyleSheet("color: #a0aec0; font-size: 12px; font-style: italic;")
        
        api_section.addWidget(api_label)
        api_section.addWidget(self.api_key_input)
        api_section.addWidget(help_text)
        
        button_layout = QVBoxLayout()
        
        self.submit_btn = QPushButton("Get Started")
        self.submit_btn.setMinimumHeight(50)
        self.submit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.submit_btn.clicked.connect(self._on_submit)
        self.submit_btn.setDefault(True)
        self.submit_btn.setObjectName("submitButton")
        
        button_layout.addWidget(self.submit_btn)
        
        layout.addStretch()
        layout.addLayout(header_layout)
        layout.addStretch()
        layout.addLayout(api_section)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.api_key_input.setFocus()
    
    def _load_from_env(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return os.getenv("OPENAI_API_KEY", "")
        except ImportError:
            return ""
    
    def _save_to_env(self, api_key):
        env_path = os.path.join(os.getcwd(), ".env")
        
        existing_lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                existing_lines = [line for line in f.readlines() if not line.startswith("OPENAI_API_KEY=")]
        
        with open(env_path, "w") as f:
            f.writelines(existing_lines)
            f.write(f"OPENAI_API_KEY={api_key}\n")
    
    def _on_submit(self):
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.api_key_input.setStyleSheet("border-color: #e53e3e !important;")
            return
        
        self._save_to_env(api_key)
        self.api_key_submitted.emit(api_key)
        self.accept()
    
    def _get_stylesheet(self):
        return """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f7fafc, stop:1 #edf2f7);
            border-radius: 20px;
        }
        
        #apiKeyInput {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 15px 20px;
            font-size: 16px;
            background-color: #ffffff;
            color: #2d3748;
            font-weight: 500;
        }
        
        #apiKeyInput:focus {
            border-color: #3182ce;
            background-color: #ffffff;
        }
        
        #submitButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3182ce, stop:1 #2c5aa0);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: 600;
            min-width: 120px;
        }
        
        #submitButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2c5aa0, stop:1 #2a4d8c);
        }
        
        #submitButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a4d8c, stop:1 #1e3a8a);
        }
        """
