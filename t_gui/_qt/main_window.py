"""
Main window for T-GUI application.
"""

from typing import Optional
try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
        QMenuBar, QMenu, QAction, QStatusBar, QDockWidget, QMessageBox,
        QFileDialog, QApplication
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QKeySequence
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
            QMenuBar, QMenu, QAction, QStatusBar, QDockWidget, QMessageBox,
            QFileDialog, QApplication
        )
        from PySide2.QtCore import Qt, Signal as pyqtSignal
        from PySide2.QtGui import QKeySequence
    except ImportError:
        raise ImportError("No Qt backend found. Please install PyQt5 or PySide2.")

from ..components.viewer import Viewer
from ..components.layer_list import LayerList
from ..app_model.context import get_app_context
from ..app_model.actions import get_action_manager
from ..plugins.manager import get_plugin_manager
from .widgets.viewer_widget import ViewerWidget
from .widgets.layer_list_widget import LayerListWidget


class MainWindow(QMainWindow):
    """
    Main application window for T-GUI.
    
    The MainWindow provides the primary user interface, including
    menus, toolbars, dock widgets, and the central viewer area.
    """
    
    viewer_changed = pyqtSignal(object)  # Viewer
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._current_viewer: Optional[Viewer] = None
        self._layer_list: Optional[LayerList] = None
        self._context = get_app_context()
        self._action_manager = get_action_manager()
        self._plugin_manager = get_plugin_manager()
        
        self._setup_ui()
        self._setup_menus()
        self._setup_actions()
        self._setup_dock_widgets()
        self._connect_signals()
        
        # Create default viewer
        self.new_viewer()
    
    def _setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("T-GUI")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # Viewer widget
        self.viewer_widget = ViewerWidget()
        self.main_splitter.addWidget(self.viewer_widget)
        
        # Set splitter proportions
        self.main_splitter.setSizes([800, 200])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _setup_menus(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        self.new_action = QAction("&New Viewer", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_viewer)
        file_menu.addAction(self.new_action)
        
        file_menu.addSeparator()
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_action)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        self.toggle_layer_list_action = QAction("&Layer List", self)
        self.toggle_layer_list_action.setCheckable(True)
        self.toggle_layer_list_action.setChecked(True)
        view_menu.addAction(self.toggle_layer_list_action)
        
        # Plugins menu
        plugins_menu = menubar.addMenu("&Plugins")
        
        self.discover_plugins_action = QAction("&Discover Plugins", self)
        self.discover_plugins_action.triggered.connect(self.discover_plugins)
        plugins_menu.addAction(self.discover_plugins_action)
        
        self.load_plugins_action = QAction("&Load All Plugins", self)
        self.load_plugins_action.triggered.connect(self.load_all_plugins)
        plugins_menu.addAction(self.load_plugins_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)
    
    def _setup_actions(self):
        """Setup application actions."""
        # Register actions with the action manager
        from ..app_model.actions import Action
        
        actions = [
            Action("file.new", "New Viewer", self.new_viewer, shortcut="Ctrl+N"),
            Action("file.open", "Open File", self.open_file, shortcut="Ctrl+O"),
            Action("file.save", "Save File", self.save_file, shortcut="Ctrl+S"),
            Action("view.toggle_layer_list", "Toggle Layer List", self.toggle_layer_list),
            Action("plugins.discover", "Discover Plugins", self.discover_plugins),
            Action("plugins.load_all", "Load All Plugins", self.load_all_plugins),
            Action("help.about", "About", self.show_about),
        ]
        
        for action in actions:
            self._action_manager.register_action(action)
    
    def _setup_dock_widgets(self):
        """Setup dock widgets."""
        # Layer list dock widget
        self.layer_list_dock = QDockWidget("Layers", self)
        self.layer_list_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.layer_list_widget = LayerListWidget()
        self.layer_list_dock.setWidget(self.layer_list_widget)
        
        self.addDockWidget(Qt.RightDockWidgetArea, self.layer_list_dock)
        
        # Connect dock widget visibility to menu action
        self.toggle_layer_list_action.toggled.connect(
            self.layer_list_dock.setVisible
        )
        self.layer_list_dock.visibilityChanged.connect(
            self.toggle_layer_list_action.setChecked
        )
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect context events
        self._context.connect('viewer_added', self._on_viewer_added)
        self._context.connect('viewer_removed', self._on_viewer_removed)
        self._context.connect('active_viewer_changed', self._on_active_viewer_changed)
        
        # Connect plugin events
        self._context.connect('widget_contributions', self._on_widget_contributions)
        self._context.connect('menu_contributions', self._on_menu_contributions)
    
    def new_viewer(self):
        """Create a new viewer."""
        viewer = Viewer(title=f"Viewer {len(self._context.viewers) + 1}")
        self.set_viewer(viewer)
        self.status_bar.showMessage(f"Created new viewer: {viewer.title}")
    
    def set_viewer(self, viewer: Optional[Viewer]):
        """
        Set the current viewer.
        
        Parameters
        ----------
        viewer : Viewer or None
            The viewer to set as current.
        """
        self._current_viewer = viewer
        self.viewer_widget.set_viewer(viewer)
        
        if viewer:
            # Create or update layer list
            if not self._layer_list:
                self._layer_list = LayerList(viewer)
            else:
                self._layer_list.set_viewer(viewer)
            
            self.layer_list_widget.set_layer_list(self._layer_list)
            self._context.active_viewer = viewer
        
        self.viewer_changed.emit(viewer)
    
    def open_file(self):
        """Open a file dialog to load data."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*.*)"
        )
        
        if file_path:
            # This is a placeholder - actual file loading would depend on file type
            self.status_bar.showMessage(f"Opened: {file_path}")
            
            # For demonstration, add a dummy layer
            if self._current_viewer:
                import numpy as np
                dummy_data = np.random.random((100, 100))
                self._current_viewer.add_image(dummy_data, name=f"Data from {file_path}")
    
    def save_file(self):
        """Save current data to file."""
        if not self._current_viewer or not self._current_viewer.layers:
            QMessageBox.information(self, "Save", "No data to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "All Files (*.*)"
        )
        
        if file_path:
            # This is a placeholder - actual saving would depend on data type
            self.status_bar.showMessage(f"Saved: {file_path}")
    
    def toggle_layer_list(self):
        """Toggle layer list visibility."""
        self.layer_list_dock.setVisible(not self.layer_list_dock.isVisible())
    
    def discover_plugins(self):
        """Discover available plugins."""
        self._plugin_manager.discover_plugins()
        plugins = self._plugin_manager.registry.get_all_plugins()
        self.status_bar.showMessage(f"Discovered {len(plugins)} plugins")
    
    def load_all_plugins(self):
        """Load all available plugins."""
        self._plugin_manager.load_all_plugins()
        loaded = self._plugin_manager.get_loaded_plugins()
        self.status_bar.showMessage(f"Loaded {len(loaded)} plugins")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About T-GUI",
            "T-GUI v0.1.0\n\n"
            "A napari-like framework for building extensible GUI applications.\n\n"
            "Built with Qt and Python."
        )
    
    def _on_viewer_added(self, event):
        """Handle viewer added event."""
        pass
    
    def _on_viewer_removed(self, event):
        """Handle viewer removed event."""
        pass
    
    def _on_active_viewer_changed(self, event):
        """Handle active viewer changed event."""
        viewer = event.data['viewer']
        if viewer != self._current_viewer:
            self.set_viewer(viewer)
    
    def _on_widget_contributions(self, event):
        """Handle widget contributions from plugins."""
        plugin_name = event.data['plugin_name']
        contributions = event.data['contributions']
        
        for contrib in contributions:
            # Add widget contributions as dock widgets
            widget_class = contrib['widget']
            name = contrib['name']
            area = contrib.get('area', 'right')
            
            try:
                widget = widget_class()
                dock = QDockWidget(name, self)
                dock.setWidget(widget)
                
                # Determine dock area
                if area == 'left':
                    dock_area = Qt.LeftDockWidgetArea
                elif area == 'right':
                    dock_area = Qt.RightDockWidgetArea
                elif area == 'bottom':
                    dock_area = Qt.BottomDockWidgetArea
                else:
                    dock_area = Qt.RightDockWidgetArea
                
                self.addDockWidget(dock_area, dock)
                
            except Exception as e:
                print(f"Error adding widget contribution from {plugin_name}: {e}")
    
    def _on_menu_contributions(self, event):
        """Handle menu contributions from plugins."""
        plugin_name = event.data['plugin_name']
        contributions = event.data['contributions']
        
        for contrib in contributions:
            # Add menu contributions
            menu_path = contrib['menu']
            action_id = contrib['action']
            shortcut = contrib.get('shortcut')
            
            try:
                # Parse menu path and add action
                # This is a simplified implementation
                menu_parts = menu_path.split('/')
                if len(menu_parts) >= 2:
                    menu_name = menu_parts[0]
                    action_name = menu_parts[1]
                    
                    # Find or create menu
                    menu = None
                    for action in self.menuBar().actions():
                        if action.text().replace('&', '') == menu_name:
                            menu = action.menu()
                            break
                    
                    if not menu:
                        menu = self.menuBar().addMenu(menu_name)
                    
                    # Add action to menu
                    action = QAction(action_name, self)
                    if shortcut:
                        action.setShortcut(shortcut)
                    action.triggered.connect(
                        lambda: self._action_manager.execute_action(action_id)
                    )
                    menu.addAction(action)
                    
            except Exception as e:
                print(f"Error adding menu contribution from {plugin_name}: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up resources
        if self._current_viewer:
            self._current_viewer.close()
        
        # Unload all plugins
        self._plugin_manager.unload_all_plugins()
        
        event.accept()
