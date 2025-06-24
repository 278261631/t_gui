"""
Main viewer component for T-GUI.
"""

from typing import Any, Dict, List, Optional
from ..events import EventEmitter
from ..app_model.context import get_app_context


class Layer:
    """
    Base class for layers in the viewer.
    
    Attributes
    ----------
    name : str
        Name of the layer.
    data : Any
        The layer data.
    visible : bool
        Whether the layer is visible.
    opacity : float
        Layer opacity (0.0 to 1.0).
    """
    
    def __init__(self, data: Any, name: str = None, visible: bool = True, opacity: float = 1.0):
        self.data = data
        self.name = name or "Layer"
        self.visible = visible
        self.opacity = opacity
        self._metadata = {}
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get layer metadata."""
        return self._metadata
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value."""
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self._metadata.get(key, default)


class ImageLayer(Layer):
    """Layer for displaying image data."""

    def __init__(self, data: Any, **kwargs):
        # Extract image-specific kwargs before passing to parent
        self.colormap = kwargs.pop('colormap', 'gray')
        self.contrast_limits = kwargs.pop('contrast_limits', None)
        super().__init__(data, **kwargs)


class PointsLayer(Layer):
    """Layer for displaying point data."""

    def __init__(self, data: Any, **kwargs):
        # Extract points-specific kwargs before passing to parent
        self.size = kwargs.pop('size', 10)
        self.edge_color = kwargs.pop('edge_color', 'black')
        self.face_color = kwargs.pop('face_color', 'white')
        super().__init__(data, **kwargs)


class Viewer(EventEmitter):
    """
    Main viewer component for displaying and interacting with data.
    
    The Viewer is the central component that manages layers, handles
    user interactions, and coordinates with other components.
    """
    
    def __init__(self, title: str = "T-GUI Viewer"):
        super().__init__()
        self.title = title
        self._layers: List[Layer] = []
        self._active_layer: Optional[Layer] = None
        self._context = get_app_context()
        
        # Register this viewer with the application context
        self._context.add_viewer(self)
    
    @property
    def layers(self) -> List[Layer]:
        """Get all layers."""
        return self._layers.copy()
    
    @property
    def active_layer(self) -> Optional[Layer]:
        """Get the active layer."""
        return self._active_layer
    
    @active_layer.setter
    def active_layer(self, layer: Optional[Layer]):
        """Set the active layer."""
        if layer is None or layer in self._layers:
            old_layer = self._active_layer
            self._active_layer = layer
            self.emit('active_layer_changed', layer=layer, old_layer=old_layer)
    
    def add_layer(self, layer: Layer, active: bool = True) -> Layer:
        """
        Add a layer to the viewer.
        
        Parameters
        ----------
        layer : Layer
            The layer to add.
        active : bool, optional
            Whether to make this layer active. Default is True.
            
        Returns
        -------
        Layer
            The added layer.
        """
        self._layers.append(layer)
        
        if active or self._active_layer is None:
            self.active_layer = layer
        
        self.emit('layer_added', layer=layer)
        return layer
    
    def remove_layer(self, layer: Layer):
        """
        Remove a layer from the viewer.
        
        Parameters
        ----------
        layer : Layer
            The layer to remove.
        """
        if layer in self._layers:
            self._layers.remove(layer)
            
            if self._active_layer is layer:
                self.active_layer = self._layers[-1] if self._layers else None
            
            self.emit('layer_removed', layer=layer)
    
    def add_image(self, data: Any, **kwargs) -> ImageLayer:
        """
        Add an image layer.
        
        Parameters
        ----------
        data : Any
            Image data.
        **kwargs
            Additional layer properties.
            
        Returns
        -------
        ImageLayer
            The created image layer.
        """
        layer = ImageLayer(data, **kwargs)
        return self.add_layer(layer)
    
    def add_points(self, data: Any, **kwargs) -> PointsLayer:
        """
        Add a points layer.
        
        Parameters
        ----------
        data : Any
            Points data.
        **kwargs
            Additional layer properties.
            
        Returns
        -------
        PointsLayer
            The created points layer.
        """
        layer = PointsLayer(data, **kwargs)
        return self.add_layer(layer)
    
    def clear_layers(self):
        """Remove all layers."""
        layers_to_remove = self._layers.copy()
        for layer in layers_to_remove:
            self.remove_layer(layer)
    
    def get_layer_by_name(self, name: str) -> Optional[Layer]:
        """
        Get a layer by name.
        
        Parameters
        ----------
        name : str
            Name of the layer.
            
        Returns
        -------
        Layer or None
            The layer if found.
        """
        for layer in self._layers:
            if layer.name == name:
                return layer
        return None
    
    def move_layer(self, layer: Layer, index: int):
        """
        Move a layer to a new position.
        
        Parameters
        ----------
        layer : Layer
            The layer to move.
        index : int
            New position index.
        """
        if layer in self._layers:
            self._layers.remove(layer)
            self._layers.insert(index, layer)
            self.emit('layer_moved', layer=layer, index=index)
    
    def close(self):
        """Close the viewer and clean up resources."""
        self._context.remove_viewer(self)
        self.emit('viewer_closed')
