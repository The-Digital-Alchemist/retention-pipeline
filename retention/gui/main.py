import sys
from PySide6.QtWidgets import QApplication
from .windows.api_key_window import APIKeySplash
from .windows.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Retention Pipeline")
    
    splash = APIKeySplash()
    main_window = None
    
    def on_api_key_submitted(api_key):
        nonlocal main_window
        main_window = MainWindow(api_key)
        
        main_window.record_requested.connect(main_window.start_recording)
        main_window.stop_requested.connect(main_window.stop_recording)
        
        main_window.show()
        
        screen = app.primaryScreen().geometry()
        x = (screen.width() - main_window.width()) // 2
        y = 50
        main_window.move(x, y)
    
    splash.api_key_submitted.connect(on_api_key_submitted)
    
    if splash.exec():
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
