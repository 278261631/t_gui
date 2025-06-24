"""
Application context management.
"""

from typing import Any, Dict, Optional
from ..events import EventEmitter


class AppContext(EventEmitter):
    """
    Manages application-wide context and state.
    
    The AppContext serves as a central hub for application state,
    providing a way for different components to share data and
    communicate changes.
    """
    
    def __init__(self):
        super().__init__()
        self._data: Dict[str, Any] = {}
        self._viewers = []
        self._active_viewer = None
    
    def set(self, key: str, value: Any):
        """
        Set a context value.
        
        Parameters
        ----------
        key : str
            The context key.
        value : Any
            The value to set.
        """
        old_value = self._data.get(key)
        self._data[key] = value
        
        # Emit change event
        self.emit('context_changed', key=key, value=value, old_value=old_value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.
        
        Parameters
        ----------
        key : str
            The context key.
        default : Any, optional
            Default value if key is not found.
            
        Returns
        -------
        Any
            The context value.
        """
        return self._data.get(key, default)
    
    def has(self, key: str) -> bool:
        """
        Check if a context key exists.
        
        Parameters
        ----------
        key : str
            The context key to check.
            
        Returns
        -------
        bool
            True if the key exists.
        """
        return key in self._data
    
    def remove(self, key: str) -> Any:
        """
        Remove a context value.
        
        Parameters
        ----------
        key : str
            The context key to remove.
            
        Returns
        -------
        Any
            The removed value, or None if key didn't exist.
        """
        old_value = self._data.pop(key, None)
        if old_value is not None:
            self.emit('context_removed', key=key, value=old_value)
        return old_value
    
    def add_viewer(self, viewer):
        """
        Add a viewer to the context.
        
        Parameters
        ----------
        viewer : Viewer
            The viewer to add.
        """
        if viewer not in self._viewers:
            self._viewers.append(viewer)
            if self._active_viewer is None:
                self._active_viewer = viewer
            self.emit('viewer_added', viewer=viewer)
    
    def remove_viewer(self, viewer):
        """
        Remove a viewer from the context.
        
        Parameters
        ----------
        viewer : Viewer
            The viewer to remove.
        """
        if viewer in self._viewers:
            self._viewers.remove(viewer)
            if self._active_viewer is viewer:
                self._active_viewer = self._viewers[0] if self._viewers else None
            self.emit('viewer_removed', viewer=viewer)
    
    @property
    def active_viewer(self):
        """Get the currently active viewer."""
        return self._active_viewer
    
    @active_viewer.setter
    def active_viewer(self, viewer):
        """Set the active viewer."""
        if viewer in self._viewers:
            old_viewer = self._active_viewer
            self._active_viewer = viewer
            self.emit('active_viewer_changed', viewer=viewer, old_viewer=old_viewer)
    
    @property
    def viewers(self):
        """Get all viewers."""
        return self._viewers.copy()
    
    def clear(self):
        """Clear all context data."""
        old_data = self._data.copy()
        self._data.clear()
        self.emit('context_cleared', old_data=old_data)


# Global application context instance
_global_context = AppContext()

def get_app_context() -> AppContext:
    """Get the global application context."""
    return _global_context
