"""
Core event system implementation.
"""

from typing import Any, Callable, Dict, List, Optional
import weakref
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Event:
    """
    Represents an event that can be emitted and handled.
    
    Attributes
    ----------
    type : str
        The type/name of the event.
    source : Any
        The object that emitted the event.
    data : Dict[str, Any]
        Additional data associated with the event.
    """
    type: str
    source: Any = None
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class EventEmitter:
    """
    Base class for objects that can emit events.
    """
    
    def __init__(self):
        self._event_manager = EventManager()
    
    def connect(self, event_type: str, callback: Callable[[Event], None]):
        """Connect a callback to an event type."""
        self._event_manager.connect(event_type, callback)
    
    def disconnect(self, event_type: str, callback: Callable[[Event], None]):
        """Disconnect a callback from an event type."""
        self._event_manager.disconnect(event_type, callback)
    
    def emit(self, event_type: str, **data):
        """Emit an event with optional data."""
        event = Event(type=event_type, source=self, data=data)
        self._event_manager.emit(event)


class EventManager:
    """
    Manages event connections and emission.
    """
    
    def __init__(self):
        # Use defaultdict with list to store multiple callbacks per event type
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        # Use weak references to avoid memory leaks
        self._weak_callbacks: Dict[str, List[weakref.ref]] = defaultdict(list)
    
    def connect(self, event_type: str, callback: Callable[[Event], None], weak: bool = True):
        """
        Connect a callback to an event type.
        
        Parameters
        ----------
        event_type : str
            The type of event to listen for.
        callback : Callable
            The function to call when the event is emitted.
        weak : bool, optional
            Whether to use weak references. Default is True.
        """
        if weak:
            # Use weak reference to avoid memory leaks
            weak_ref = weakref.ref(callback)
            self._weak_callbacks[event_type].append(weak_ref)
        else:
            self._callbacks[event_type].append(callback)
    
    def disconnect(self, event_type: str, callback: Callable[[Event], None]):
        """
        Disconnect a callback from an event type.
        
        Parameters
        ----------
        event_type : str
            The type of event to stop listening for.
        callback : Callable
            The function to disconnect.
        """
        # Remove from strong references
        if callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)
        
        # Remove from weak references
        to_remove = []
        for weak_ref in self._weak_callbacks[event_type]:
            if weak_ref() is callback:
                to_remove.append(weak_ref)
        
        for weak_ref in to_remove:
            self._weak_callbacks[event_type].remove(weak_ref)
    
    def emit(self, event: Event):
        """
        Emit an event to all connected callbacks.
        
        Parameters
        ----------
        event : Event
            The event to emit.
        """
        # Call strong reference callbacks
        for callback in self._callbacks[event.type]:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")
        
        # Call weak reference callbacks (clean up dead references)
        to_remove = []
        for weak_ref in self._weak_callbacks[event.type]:
            callback = weak_ref()
            if callback is None:
                # Dead reference, mark for removal
                to_remove.append(weak_ref)
            else:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
        
        # Clean up dead weak references
        for weak_ref in to_remove:
            self._weak_callbacks[event.type].remove(weak_ref)
    
    def clear(self, event_type: Optional[str] = None):
        """
        Clear all callbacks for a specific event type or all event types.
        
        Parameters
        ----------
        event_type : str, optional
            The event type to clear. If None, clears all event types.
        """
        if event_type is None:
            self._callbacks.clear()
            self._weak_callbacks.clear()
        else:
            self._callbacks[event_type].clear()
            self._weak_callbacks[event_type].clear()


# Global event manager instance
_global_event_manager = EventManager()

def get_global_event_manager() -> EventManager:
    """Get the global event manager instance."""
    return _global_event_manager
