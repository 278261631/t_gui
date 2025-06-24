"""
Application model for T-GUI.

This module defines the application-level model, including actions, context,
and application state management.
"""

from .context import AppContext
from .actions import ActionManager

__all__ = ['AppContext', 'ActionManager']
