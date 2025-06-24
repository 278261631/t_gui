"""
Qt-based user interface for T-GUI.

This module contains all Qt-specific code for the user interface,
keeping it separate from the core application logic.
"""

import sys
from typing import Optional

# Qt imports with fallback support
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    QT_BACKEND = "PyQt5"
except ImportError:
    try:
        from PySide2.QtWidgets import QApplication
        from PySide2.QtCore import Qt
        QT_BACKEND = "PySide2"
    except ImportError:
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            QT_BACKEND = "PyQt6"
        except ImportError:
            try:
                from PySide6.QtWidgets import QApplication
                from PySide6.QtCore import Qt
                QT_BACKEND = "PySide6"
            except ImportError:
                raise ImportError(
                    "No Qt backend found. Please install PyQt5, PySide2, PyQt6, or PySide6."
                )

from .main_window import MainWindow
from .widgets import *

# Global application instance
_app_instance: Optional[QApplication] = None


def get_app() -> QApplication:
    """
    Get or create the Qt application instance.
    
    Returns
    -------
    QApplication
        The Qt application instance.
    """
    global _app_instance
    
    if _app_instance is None:
        # Check if an application already exists
        existing_app = QApplication.instance()
        if existing_app is not None:
            _app_instance = existing_app
        else:
            # Create new application
            _app_instance = QApplication(sys.argv)
            _app_instance.setApplicationName("T-GUI")
            _app_instance.setApplicationVersion("0.1.0")
            _app_instance.setOrganizationName("T-GUI")
    
    return _app_instance


def set_app_style(style_name: str = "Fusion"):
    """
    Set the application style.
    
    Parameters
    ----------
    style_name : str, optional
        Name of the style to use. Default is "Fusion".
    """
    app = get_app()
    app.setStyle(style_name)


def apply_dark_theme():
    """Apply a dark theme to the application."""
    app = get_app()

    # Dark palette - import based on available backend
    try:
        from PyQt5.QtGui import QPalette, QColor
        from PyQt5.QtCore import Qt
    except ImportError:
        try:
            from PySide2.QtGui import QPalette, QColor
            from PySide2.QtCore import Qt
        except ImportError:
            print("Warning: Could not apply dark theme - no Qt backend found")
            return
    
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    
    # Base colors
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    
    # Text colors
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    
    # Button colors
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    
    # Highlight colors
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(palette)


__all__ = [
    'get_app',
    'set_app_style', 
    'apply_dark_theme',
    'MainWindow',
    'QT_BACKEND'
]
