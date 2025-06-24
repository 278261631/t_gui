# T-GUI: A napari-like Framework

T-GUI is a flexible, extensible framework for building GUI applications with plugin support, inspired by napari. It provides a solid foundation for creating scientific and data visualization applications with a modern, plugin-based architecture.

## Features

- **Plugin System**: Extensible plugin architecture using pluggy
- **Event System**: Robust event handling for component communication
- **Layer Management**: Hierarchical layer system for data visualization
- **Qt-based UI**: Modern user interface built with Qt (supports PyQt5/6, PySide2/6)
- **Settings Management**: Persistent configuration system
- **Action System**: Reusable command system with menu/toolbar integration

## Installation

### From Source

```bash
git clone https://github.com/your-username/t-gui.git
cd t-gui
pip install -e .
```

### Dependencies

- Python 3.7+
- PyQt5/PyQt6 or PySide2/PySide6
- pluggy
- numpy

## Quick Start

### Basic Usage

```python
import numpy as np
import t_gui

# Create a viewer
viewer = t_gui.make_viewer()

# Add some data
image_data = np.random.random((100, 100))
viewer.add_image(image_data, name="Random Image")

points_data = np.random.random((50, 2)) * 100
viewer.add_points(points_data, name="Random Points")

# Launch the application
t_gui.run()
```

### Using the Main Window

```python
import t_gui

# Create main window with viewer
window = t_gui.MainWindow()
window.show()

# The window automatically creates a default viewer
# You can access it through the window's viewer_widget
```

## Architecture

### Core Components

- **Viewer**: Central component for displaying and managing layers
- **LayerList**: Component for managing layer hierarchy and selection
- **EventSystem**: Handles communication between components
- **PluginManager**: Manages plugin loading and contributions
- **Settings**: Persistent configuration management

### Plugin System

T-GUI uses a hook-based plugin system similar to napari. Plugins can contribute:

- **Widgets**: Custom UI components
- **Actions**: Reusable commands
- **Menu Items**: Menu contributions
- **File Readers/Writers**: Data I/O functionality

### Example Plugin

```python
from t_gui.plugins.hookspecs import hookspec

class MyPlugin:
    @hookspec
    def t_gui_get_widget_contributions(self):
        return [{
            'widget': MyCustomWidget,
            'name': 'My Widget',
            'area': 'right'
        }]
    
    @hookspec
    def t_gui_get_action_contributions(self):
        return [{
            'id': 'my.action',
            'title': 'My Action',
            'callback': self.my_action_callback
        }]
    
    def my_action_callback(self):
        print("Action executed!")

def setup_plugin():
    return MyPlugin()
```

## Layer Types

### Image Layers

```python
# Add image data
viewer.add_image(image_array, name="My Image", colormap='viridis')
```

### Points Layers

```python
# Add point data
viewer.add_points(points_array, name="My Points", size=10, face_color='red')
```

### Custom Layers

You can create custom layer types by inheriting from the base `Layer` class:

```python
from t_gui.components.viewer import Layer

class CustomLayer(Layer):
    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        # Custom layer implementation
```

## Event System

T-GUI provides a robust event system for component communication:

```python
# Connect to events
def on_layer_added(event):
    layer = event.data['layer']
    print(f"Layer added: {layer.name}")

viewer.connect('layer_added', on_layer_added)

# Emit custom events
viewer.emit('custom_event', data={'key': 'value'})
```

## Settings

T-GUI includes a persistent settings system:

```python
from t_gui.settings import get_settings

settings = get_settings()

# Get setting
theme = settings.get('appearance.theme')

# Set setting
settings.set('appearance.theme', 'dark')

# Listen for changes
def on_setting_changed(event):
    print(f"Setting {event.data['key']} changed to {event.data['value']}")

settings.connect('setting_changed', on_setting_changed)
```

## Examples

See the `examples/` directory for more detailed examples:

- `basic_usage.py`: Basic application usage
- `plugin_example.py`: Complete plugin example

## Development

### Running Tests

```bash
pip install -e .[dev]
pytest
```

### Code Style

```bash
black t_gui/
flake8 t_gui/
```

### Building Documentation

```bash
pip install -e .[docs]
cd docs/
make html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by [napari](https://napari.org/)
- Built with [Qt](https://www.qt.io/) and [pluggy](https://pluggy.readthedocs.io/)
