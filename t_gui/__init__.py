"""
T-GUI: A napari-like framework for building extensible GUI applications.

This package provides a framework for creating GUI applications with plugin support,
similar to napari but more general-purpose.
"""

__version__ = "0.1.0"

from .components.viewer import Viewer
from .app_model.context import AppContext
from ._qt.main_window import MainWindow
from .plugins.manager import PluginManager

# Main application entry point
def run(*, show=True, block=True):
    """
    Launch the T-GUI application.
    
    Parameters
    ----------
    show : bool, optional
        Whether to show the main window immediately. Default is True.
    block : bool, optional
        Whether to block execution until the window is closed. Default is True.
        
    Returns
    -------
    MainWindow
        The main application window.
    """
    from ._qt import get_app
    
    app = get_app()
    window = MainWindow()
    
    if show:
        window.show()
    
    if block:
        app.exec_()
    
    return window

def make_viewer(**kwargs):
    """
    Create a new viewer instance.
    
    Parameters
    ----------
    **kwargs
        Additional arguments passed to the Viewer constructor.
        
    Returns
    -------
    Viewer
        A new viewer instance.
    """
    return Viewer(**kwargs)

# Convenience imports for common use cases
__all__ = [
    'run',
    'make_viewer',
    'Viewer',
    'MainWindow',
    'AppContext',
    'PluginManager',
]
