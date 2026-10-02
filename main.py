import sys
import os

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    from utils.logger import logger

    logger.info("Starting Quantyx application")
    app = QApplication(sys.argv)
    
    # Modern style
    from utils.theme_manager import ThemeManager
    from utils.config import load_settings
    settings = load_settings()
    is_dark = settings.get('is_dark_theme', True)
    ThemeManager.set_theme(is_dark)
    
    from PyQt6.QtGui import QIcon
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, "img", "app-ico-1.ico")
    else:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "app-ico-1.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
