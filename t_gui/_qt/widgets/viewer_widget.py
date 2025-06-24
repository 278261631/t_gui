"""
Qt widget for the main viewer display.
"""

from typing import Optional
try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPainter, QColor, QFont
except ImportError:
    try:
        from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
        from PySide2.QtCore import Qt, Signal as pyqtSignal
        from PySide2.QtGui import QPainter, QColor, QFont
    except ImportError:
        raise ImportError("No Qt backend found. Please install PyQt5 or PySide2.")

from ...components.viewer import Viewer, Layer


class ViewerCanvas(QWidget):
    """
    Canvas widget for displaying viewer content.
    
    This is a simplified canvas that can be extended with actual
    rendering capabilities (e.g., using OpenGL, matplotlib, etc.)
    """
    
    layer_clicked = pyqtSignal(object)  # Layer
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
        self._viewer: Optional[Viewer] = None
        self._layers_info = []
    
    def set_viewer(self, viewer: Optional[Viewer]):
        """
        Set the viewer to display.
        
        Parameters
        ----------
        viewer : Viewer or None
            The viewer to display.
        """
        if self._viewer:
            # Disconnect from old viewer
            self._viewer.disconnect('layer_added', self._on_layer_changed)
            self._viewer.disconnect('layer_removed', self._on_layer_changed)
            self._viewer.disconnect('active_layer_changed', self._on_active_layer_changed)
        
        self._viewer = viewer
        
        if self._viewer:
            # Connect to new viewer
            self._viewer.connect('layer_added', self._on_layer_changed)
            self._viewer.connect('layer_removed', self._on_layer_changed)
            self._viewer.connect('active_layer_changed', self._on_active_layer_changed)
        
        self._update_layers_info()
        self.update()
    
    def _update_layers_info(self):
        """Update the layers information for display."""
        self._layers_info = []
        if self._viewer:
            for i, layer in enumerate(self._viewer.layers):
                info = {
                    'layer': layer,
                    'name': layer.name,
                    'type': type(layer).__name__,
                    'visible': layer.visible,
                    'opacity': layer.opacity,
                    'is_active': layer is self._viewer.active_layer
                }
                self._layers_info.append(info)
    
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(43, 43, 43))
        
        if not self._viewer or not self._layers_info:
            # Draw placeholder text
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data to display")
            return
        
        # Draw layer information (simplified visualization)
        y_offset = 20
        painter.setFont(QFont("Arial", 10))
        
        for info in self._layers_info:
            if not info['visible']:
                continue
            
            # Set color based on layer type and activity
            if info['is_active']:
                painter.setPen(QColor(100, 150, 255))
            else:
                painter.setPen(QColor(200, 200, 200))
            
            # Draw layer representation
            text = f"{info['name']} ({info['type']})"
            painter.drawText(10, y_offset, text)
            
            # Draw opacity indicator
            opacity_width = int(100 * info['opacity'])
            painter.fillRect(10, y_offset + 5, opacity_width, 3, 
                           QColor(100, 150, 255, int(255 * info['opacity'])))
            
            y_offset += 30
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton and self._viewer:
            # Simple layer selection based on click position
            y_pos = event.y()
            layer_index = (y_pos - 20) // 30
            
            if 0 <= layer_index < len(self._layers_info):
                layer_info = self._layers_info[layer_index]
                self.layer_clicked.emit(layer_info['layer'])
                self._viewer.active_layer = layer_info['layer']
    
    def _on_layer_changed(self, event):
        """Handle layer changes."""
        self._update_layers_info()
        self.update()
    
    def _on_active_layer_changed(self, event):
        """Handle active layer changes."""
        self._update_layers_info()
        self.update()


class ViewerWidget(QWidget):
    """
    Main viewer widget that contains the canvas and controls.
    """
    
    def __init__(self, viewer: Optional[Viewer] = None, parent=None):
        super().__init__(parent)
        self._viewer: Optional[Viewer] = None
        
        self._setup_ui()
        
        if viewer:
            self.set_viewer(viewer)
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with viewer title
        self.header_frame = QFrame()
        self.header_frame.setFrameStyle(QFrame.StyledPanel)
        self.header_frame.setMaximumHeight(30)
        
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(5, 2, 5, 2)
        
        self.title_label = QLabel("Viewer")
        self.title_label.setStyleSheet("font-weight: bold; color: #ddd;")
        header_layout.addWidget(self.title_label)
        
        layout.addWidget(self.header_frame)
        
        # Main canvas
        self.canvas = ViewerCanvas()
        layout.addWidget(self.canvas, 1)
        
        # Connect canvas signals
        self.canvas.layer_clicked.connect(self._on_layer_clicked)
    
    def set_viewer(self, viewer: Optional[Viewer]):
        """
        Set the viewer to display.
        
        Parameters
        ----------
        viewer : Viewer or None
            The viewer to display.
        """
        self._viewer = viewer
        self.canvas.set_viewer(viewer)
        
        if viewer:
            self.title_label.setText(viewer.title)
        else:
            self.title_label.setText("Viewer")
    
    @property
    def viewer(self) -> Optional[Viewer]:
        """Get the current viewer."""
        return self._viewer
    
    def _on_layer_clicked(self, layer: Layer):
        """Handle layer click in canvas."""
        # This could emit a signal or perform other actions
        pass
