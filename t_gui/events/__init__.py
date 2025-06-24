"""
Event system for T-GUI.

This module provides a simple but powerful event system for communication
between different parts of the application and plugins.
"""

from .event_system import Event, EventEmitter, EventManager

__all__ = ['Event', 'EventEmitter', 'EventManager']
