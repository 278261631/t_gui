"""
Qt widget for displaying and managing layers.
"""

from typing import Optional, List
try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
        QPushButton, QLabel, QSlider, QCheckBox, QMenu, QAction
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QIcon
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
            QPushButton, QLabel, QSlider, QCheckBox, QMenu, QAction
        )
        from PySide2.QtCore import Qt, Signal as pyqtSignal
        from PySide2.QtGui import QIcon
    except ImportError:
        raise ImportError("No Qt backend found. Please install PyQt5 or PySide2.")

from ...components.layer_list import LayerList
from ...components.viewer import Layer, Viewer


class LayerItemWidget(QWidget):
    """Widget for displaying a single layer item."""
    
    visibility_changed = pyqtSignal(bool)
    opacity_changed = pyqtSignal(float)
    
    def __init__(self, layer: Layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Visibility checkbox
        self.visibility_checkbox = QCheckBox()
        self.visibility_checkbox.setChecked(self.layer.visible)
        layout.addWidget(self.visibility_checkbox)
        
        # Layer name label
        self.name_label = QLabel(self.layer.name)
        layout.addWidget(self.name_label, 1)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.layer.opacity * 100))
        self.opacity_slider.setMaximumWidth(80)
        layout.addWidget(self.opacity_slider)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.visibility_checkbox.toggled.connect(self.visibility_changed)
        self.opacity_slider.valueChanged.connect(
            lambda value: self.opacity_changed.emit(value / 100.0)
        )
    
    def update_layer(self):
        """Update widget to reflect layer state."""
        self.visibility_checkbox.setChecked(self.layer.visible)
        self.opacity_slider.setValue(int(self.layer.opacity * 100))
        self.name_label.setText(self.layer.name)


class LayerListWidget(QWidget):
    """
    Qt widget for displaying and managing a list of layers.
    """
    
    layer_selected = pyqtSignal(object)  # Layer
    layer_double_clicked = pyqtSignal(object)  # Layer
    
    def __init__(self, layer_list: Optional[LayerList] = None, parent=None):
        super().__init__(parent)
        self._layer_list: Optional[LayerList] = None
        self._layer_widgets = {}  # Map layer to widget
        
        self._setup_ui()
        self._setup_actions()
        
        if layer_list:
            self.set_layer_list(layer_list)
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Layers")
        header_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Add/remove buttons
        self.add_button = QPushButton("+")
        self.add_button.setMaximumSize(25, 25)
        self.remove_button = QPushButton("-")
        self.remove_button.setMaximumSize(25, 25)
        
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.remove_button)
        
        layout.addLayout(header_layout)
        
        # Layer list
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.list_widget)
        
        # Connect signals
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.remove_button.clicked.connect(self._remove_selected_layers)
    
    def _setup_actions(self):
        """Setup context menu actions."""
        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(self._remove_selected_layers)
        
        self.move_up_action = QAction("Move Up", self)
        self.move_up_action.triggered.connect(self._move_layer_up)
        
        self.move_down_action = QAction("Move Down", self)
        self.move_down_action.triggered.connect(self._move_layer_down)
        
        self.duplicate_action = QAction("Duplicate", self)
        self.duplicate_action.triggered.connect(self._duplicate_layer)
    
    def set_layer_list(self, layer_list: Optional[LayerList]):
        """
        Set the layer list to display.
        
        Parameters
        ----------
        layer_list : LayerList or None
            The layer list to display.
        """
        if self._layer_list:
            # Disconnect from old layer list
            self._layer_list.disconnect('layer_added', self._on_layer_added)
            self._layer_list.disconnect('layer_removed', self._on_layer_removed)
            self._layer_list.disconnect('layer_moved', self._on_layer_moved)
            self._layer_list.disconnect('selection_changed', self._on_layer_selection_changed)
        
        self._layer_list = layer_list
        self._refresh_list()
        
        if self._layer_list:
            # Connect to new layer list
            self._layer_list.connect('layer_added', self._on_layer_added)
            self._layer_list.connect('layer_removed', self._on_layer_removed)
            self._layer_list.connect('layer_moved', self._on_layer_moved)
            self._layer_list.connect('selection_changed', self._on_layer_selection_changed)
    
    def _refresh_list(self):
        """Refresh the entire layer list."""
        self.list_widget.clear()
        self._layer_widgets.clear()
        
        if self._layer_list:
            for layer in reversed(self._layer_list.layers):  # Reverse for top-to-bottom display
                self._add_layer_item(layer)
    
    def _add_layer_item(self, layer: Layer):
        """Add a layer item to the list."""
        item = QListWidgetItem()
        widget = LayerItemWidget(layer)
        
        # Connect layer widget signals
        widget.visibility_changed.connect(
            lambda visible: self._on_layer_visibility_changed(layer, visible)
        )
        widget.opacity_changed.connect(
            lambda opacity: self._on_layer_opacity_changed(layer, opacity)
        )
        
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        
        self._layer_widgets[layer] = (item, widget)
    
    def _remove_layer_item(self, layer: Layer):
        """Remove a layer item from the list."""
        if layer in self._layer_widgets:
            item, widget = self._layer_widgets[layer]
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)
            del self._layer_widgets[layer]
    
    def _on_layer_added(self, event):
        """Handle layer added event."""
        layer = event.data['layer']
        self._add_layer_item(layer)
    
    def _on_layer_removed(self, event):
        """Handle layer removed event."""
        layer = event.data['layer']
        self._remove_layer_item(layer)
    
    def _on_layer_moved(self, event):
        """Handle layer moved event."""
        # For simplicity, refresh the entire list
        self._refresh_list()
    
    def _on_layer_selection_changed(self, event):
        """Handle layer selection changed event."""
        # Update list widget selection to match layer list selection
        pass
    
    def _on_selection_changed(self):
        """Handle list widget selection change."""
        selected_items = self.list_widget.selectedItems()
        if selected_items and self._layer_list:
            # Find the layer corresponding to the selected item
            for layer, (item, widget) in self._layer_widgets.items():
                if item in selected_items:
                    self._layer_list.select_layer(layer)
                    self.layer_selected.emit(layer)
                    break
    
    def _on_item_double_clicked(self, item):
        """Handle item double click."""
        for layer, (layer_item, widget) in self._layer_widgets.items():
            if layer_item is item:
                self.layer_double_clicked.emit(layer)
                break
    
    def _on_layer_visibility_changed(self, layer: Layer, visible: bool):
        """Handle layer visibility change."""
        if self._layer_list:
            self._layer_list.toggle_layer_visibility(layer)
    
    def _on_layer_opacity_changed(self, layer: Layer, opacity: float):
        """Handle layer opacity change."""
        if self._layer_list:
            self._layer_list.set_layer_opacity(layer, opacity)
    
    def _show_context_menu(self, position):
        """Show context menu."""
        item = self.list_widget.itemAt(position)
        if item:
            menu = QMenu(self)
            menu.addAction(self.move_up_action)
            menu.addAction(self.move_down_action)
            menu.addSeparator()
            menu.addAction(self.duplicate_action)
            menu.addAction(self.delete_action)
            menu.exec_(self.list_widget.mapToGlobal(position))
    
    def _remove_selected_layers(self):
        """Remove selected layers."""
        if self._layer_list:
            self._layer_list.delete_selected_layers()
    
    def _move_layer_up(self):
        """Move selected layer up."""
        selected_items = self.list_widget.selectedItems()
        if selected_items and self._layer_list:
            for layer, (item, widget) in self._layer_widgets.items():
                if item in selected_items:
                    self._layer_list.move_layer_up(layer)
                    break
    
    def _move_layer_down(self):
        """Move selected layer down."""
        selected_items = self.list_widget.selectedItems()
        if selected_items and self._layer_list:
            for layer, (item, widget) in self._layer_widgets.items():
                if item in selected_items:
                    self._layer_list.move_layer_down(layer)
                    break
    
    def _duplicate_layer(self):
        """Duplicate selected layer."""
        # This would need to be implemented based on specific layer types
        pass
