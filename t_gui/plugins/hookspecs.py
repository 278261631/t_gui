"""
Plugin hook specifications.

This module defines the hook specifications that plugins can implement
to extend the application functionality.
"""

import pluggy
from typing import Any, Dict, List, Optional, Callable


# Create the hook specification namespace
hookspec = pluggy.HookspecMarker("t_gui")


class TGuiHookSpecs:
    """Hook specifications for T-GUI plugins."""
    
    @hookspec
    def t_gui_get_widget_contributions(self) -> List[Dict[str, Any]]:
        """
        Get widget contributions from the plugin.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of widget contribution dictionaries. Each dictionary should contain:
            - 'widget': The widget class or factory function
            - 'name': Display name for the widget
            - 'area': Where to place the widget ('left', 'right', 'bottom', 'floating')
        """
        pass
    
    @hookspec
    def t_gui_get_menu_contributions(self) -> List[Dict[str, Any]]:
        """
        Get menu contributions from the plugin.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of menu contribution dictionaries. Each dictionary should contain:
            - 'menu': Menu path (e.g., 'File/Open')
            - 'action': Action to execute
            - 'shortcut': Optional keyboard shortcut
        """
        pass
    
    @hookspec
    def t_gui_get_action_contributions(self) -> List[Dict[str, Any]]:
        """
        Get action contributions from the plugin.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of action contribution dictionaries. Each dictionary should contain:
            - 'id': Unique action identifier
            - 'title': Display title
            - 'callback': Function to execute
            - 'tooltip': Optional tooltip
            - 'icon': Optional icon
            - 'shortcut': Optional keyboard shortcut
        """
        pass
    
    @hookspec
    def t_gui_get_reader_contributions(self) -> List[Dict[str, Any]]:
        """
        Get file reader contributions from the plugin.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of reader contribution dictionaries. Each dictionary should contain:
            - 'function': Reader function
            - 'patterns': List of file patterns (e.g., ['*.txt', '*.csv'])
            - 'name': Display name for the reader
        """
        pass
    
    @hookspec
    def t_gui_get_writer_contributions(self) -> List[Dict[str, Any]]:
        """
        Get file writer contributions from the plugin.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of writer contribution dictionaries. Each dictionary should contain:
            - 'function': Writer function
            - 'patterns': List of file patterns (e.g., ['*.txt', '*.csv'])
            - 'name': Display name for the writer
        """
        pass
    
    @hookspec
    def t_gui_setup_plugin(self, plugin_manager) -> None:
        """
        Setup hook called when the plugin is loaded.
        
        Parameters
        ----------
        plugin_manager : PluginManager
            The plugin manager instance.
        """
        pass
    
    @hookspec
    def t_gui_teardown_plugin(self, plugin_manager) -> None:
        """
        Teardown hook called when the plugin is unloaded.
        
        Parameters
        ----------
        plugin_manager : PluginManager
            The plugin manager instance.
        """
        pass


# Create the hook specifications instance
hookspecs = TGuiHookSpecs()
