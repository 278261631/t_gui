"""
Layer list component for T-GUI.
"""

from typing import List, Optional, Callable
from ..events import EventEmitter
from .viewer import Viewer, Layer


class LayerList(EventEmitter):
    """
    Component for managing and displaying the list of layers.
    
    The LayerList provides functionality for viewing, selecting,
    and manipulating layers in a viewer.
    """
    
    def __init__(self, viewer: Optional[Viewer] = None):
        super().__init__()
        self._viewer: Optional[Viewer] = None
        self._selection: List[Layer] = []
        
        if viewer:
            self.set_viewer(viewer)
    
    @property
    def viewer(self) -> Optional[Viewer]:
        """Get the associated viewer."""
        return self._viewer
    
    @property
    def layers(self) -> List[Layer]:
        """Get all layers from the viewer."""
        if self._viewer:
            return self._viewer.layers
        return []
    
    @property
    def selection(self) -> List[Layer]:
        """Get the currently selected layers."""
        return self._selection.copy()
    
    def set_viewer(self, viewer: Optional[Viewer]):
        """
        Set the viewer to display layers from.
        
        Parameters
        ----------
        viewer : Viewer or None
            The viewer to associate with this layer list.
        """
        if self._viewer:
            # Disconnect from old viewer
            self._viewer.disconnect('layer_added', self._on_layer_added)
            self._viewer.disconnect('layer_removed', self._on_layer_removed)
            self._viewer.disconnect('layer_moved', self._on_layer_moved)
            self._viewer.disconnect('active_layer_changed', self._on_active_layer_changed)
        
        self._viewer = viewer
        self._selection.clear()
        
        if self._viewer:
            # Connect to new viewer
            self._viewer.connect('layer_added', self._on_layer_added)
            self._viewer.connect('layer_removed', self._on_layer_removed)
            self._viewer.connect('layer_moved', self._on_layer_moved)
            self._viewer.connect('active_layer_changed', self._on_active_layer_changed)
        
        self.emit('viewer_changed', viewer=viewer)
    
    def select_layer(self, layer: Layer, extend: bool = False):
        """
        Select a layer.
        
        Parameters
        ----------
        layer : Layer
            The layer to select.
        extend : bool, optional
            Whether to extend the current selection. Default is False.
        """
        if not extend:
            self._selection.clear()
        
        if layer not in self._selection and layer in self.layers:
            self._selection.append(layer)
            self.emit('selection_changed', selection=self._selection)
    
    def deselect_layer(self, layer: Layer):
        """
        Deselect a layer.
        
        Parameters
        ----------
        layer : Layer
            The layer to deselect.
        """
        if layer in self._selection:
            self._selection.remove(layer)
            self.emit('selection_changed', selection=self._selection)
    
    def clear_selection(self):
        """Clear the layer selection."""
        if self._selection:
            self._selection.clear()
            self.emit('selection_changed', selection=self._selection)
    
    def select_all(self):
        """Select all layers."""
        self._selection = self.layers.copy()
        self.emit('selection_changed', selection=self._selection)
    
    def is_selected(self, layer: Layer) -> bool:
        """
        Check if a layer is selected.
        
        Parameters
        ----------
        layer : Layer
            The layer to check.
            
        Returns
        -------
        bool
            True if the layer is selected.
        """
        return layer in self._selection
    
    def move_layer_up(self, layer: Layer):
        """
        Move a layer up in the list.
        
        Parameters
        ----------
        layer : Layer
            The layer to move up.
        """
        if self._viewer and layer in self._viewer.layers:
            layers = self._viewer.layers
            current_index = layers.index(layer)
            if current_index > 0:
                self._viewer.move_layer(layer, current_index - 1)
    
    def move_layer_down(self, layer: Layer):
        """
        Move a layer down in the list.
        
        Parameters
        ----------
        layer : Layer
            The layer to move down.
        """
        if self._viewer and layer in self._viewer.layers:
            layers = self._viewer.layers
            current_index = layers.index(layer)
            if current_index < len(layers) - 1:
                self._viewer.move_layer(layer, current_index + 1)
    
    def delete_selected_layers(self):
        """Delete all selected layers."""
        if self._viewer:
            for layer in self._selection.copy():
                self._viewer.remove_layer(layer)
    
    def toggle_layer_visibility(self, layer: Layer):
        """
        Toggle the visibility of a layer.
        
        Parameters
        ----------
        layer : Layer
            The layer to toggle.
        """
        layer.visible = not layer.visible
        self.emit('layer_visibility_changed', layer=layer, visible=layer.visible)
    
    def set_layer_opacity(self, layer: Layer, opacity: float):
        """
        Set the opacity of a layer.
        
        Parameters
        ----------
        layer : Layer
            The layer to modify.
        opacity : float
            New opacity value (0.0 to 1.0).
        """
        layer.opacity = max(0.0, min(1.0, opacity))
        self.emit('layer_opacity_changed', layer=layer, opacity=layer.opacity)
    
    def _on_layer_added(self, event):
        """Handle layer added event from viewer."""
        self.emit('layer_added', layer=event.data['layer'])
    
    def _on_layer_removed(self, event):
        """Handle layer removed event from viewer."""
        layer = event.data['layer']
        if layer in self._selection:
            self._selection.remove(layer)
        self.emit('layer_removed', layer=layer)
    
    def _on_layer_moved(self, event):
        """Handle layer moved event from viewer."""
        self.emit('layer_moved', layer=event.data['layer'], index=event.data['index'])
    
    def _on_active_layer_changed(self, event):
        """Handle active layer changed event from viewer."""
        self.emit('active_layer_changed', 
                 layer=event.data['layer'], 
                 old_layer=event.data['old_layer'])
