"""
Plugin system for T-GUI.

This module provides a flexible plugin system that allows extending
the application with custom functionality.
"""

from .manager import PluginManager
from .hookspecs import hookspecs
from .registry import PluginRegistry

__all__ = ['PluginManager', 'hookspecs', 'PluginRegistry']
