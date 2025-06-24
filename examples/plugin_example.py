"""
Example plugin for T-GUI.

This example demonstrates how to create a plugin that extends
T-GUI with custom functionality.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import pyqtSignal
import numpy as np

from t_gui.plugins.hookspecs import hookspec
from t_gui.app_model.actions import action


class ExampleWidget(QWidget):
    """Example widget that can be added as a plugin contribution."""
    
    data_generated = pyqtSignal(object)  # numpy array
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Example Plugin Widget")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Description
        description = QLabel("This widget demonstrates plugin functionality.")
        layout.addWidget(description)
        
        # Generate data button
        self.generate_button = QPushButton("Generate Random Data")
        self.generate_button.clicked.connect(self._generate_data)
        layout.addWidget(self.generate_button)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(100)
        self.log_area.setPlaceholderText("Plugin log messages will appear here...")
        layout.addWidget(self.log_area)
        
        layout.addStretch()
    
    def _generate_data(self):
        """Generate random data and emit signal."""
        data = np.random.random((100, 100))
        self.data_generated.emit(data)
        self.log_area.append("Generated 100x100 random data array")


class ExamplePlugin:
    """
    Example plugin class that implements T-GUI hook specifications.
    
    This plugin demonstrates:
    - Widget contributions
    - Action contributions
    - Menu contributions
    """
    
    def __init__(self):
        self.widget = None
    
    @hookspec
    def t_gui_get_widget_contributions(self):
        """Contribute a custom widget."""
        return [
            {
                'widget': ExampleWidget,
                'name': 'Example Plugin',
                'area': 'right'
            }
        ]
    
    @hookspec
    def t_gui_get_action_contributions(self):
        """Contribute custom actions."""
        return [
            {
                'id': 'example.hello',
                'title': 'Say Hello',
                'callback': self.say_hello,
                'tooltip': 'Display a hello message',
                'shortcut': 'Ctrl+H'
            },
            {
                'id': 'example.generate_data',
                'title': 'Generate Example Data',
                'callback': self.generate_example_data,
                'tooltip': 'Generate example data in the viewer'
            }
        ]
    
    @hookspec
    def t_gui_get_menu_contributions(self):
        """Contribute menu items."""
        return [
            {
                'menu': 'Examples/Hello',
                'action': 'example.hello',
                'shortcut': 'Ctrl+H'
            },
            {
                'menu': 'Examples/Generate Data',
                'action': 'example.generate_data'
            }
        ]
    
    @hookspec
    def t_gui_get_reader_contributions(self):
        """Contribute file readers."""
        return [
            {
                'function': self.read_example_file,
                'patterns': ['*.example', '*.ex'],
                'name': 'Example File Reader'
            }
        ]
    
    @hookspec
    def t_gui_setup_plugin(self, plugin_manager):
        """Setup the plugin when loaded."""
        print("Example plugin loaded!")
        
        # Connect to application context for viewer access
        from t_gui.app_model.context import get_app_context
        self.context = get_app_context()
    
    @hookspec
    def t_gui_teardown_plugin(self, plugin_manager):
        """Cleanup when plugin is unloaded."""
        print("Example plugin unloaded!")
    
    def say_hello(self):
        """Action callback to say hello."""
        print("Hello from the example plugin!")
        
        # You could also show a dialog, update the viewer, etc.
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Example Plugin")
        msg.setText("Hello from the example plugin!")
        msg.exec_()
    
    def generate_example_data(self):
        """Action callback to generate example data."""
        # Get the active viewer
        if self.context and self.context.active_viewer:
            viewer = self.context.active_viewer
            
            # Generate some example data
            data = np.random.random((200, 200))
            viewer.add_image(data, name="Plugin Generated Data")
            
            print("Generated example data in viewer")
        else:
            print("No active viewer found")
    
    def read_example_file(self, file_path):
        """Example file reader."""
        # This would normally read actual file data
        # For this example, we'll just generate dummy data
        print(f"Reading example file: {file_path}")
        
        # Return dummy data
        return {
            'data': np.random.random((100, 100)),
            'metadata': {
                'file_path': file_path,
                'file_type': 'example'
            }
        }


# Plugin entry point
def setup_plugin():
    """
    Plugin entry point function.
    
    This function is called when the plugin is loaded.
    It should return the plugin instance.
    """
    return ExamplePlugin()


# For testing the plugin standalone
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the example widget
    widget = ExampleWidget()
    widget.show()
    
    sys.exit(app.exec_())
