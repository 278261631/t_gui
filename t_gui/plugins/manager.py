"""
Plugin manager for T-GUI.
"""

import pluggy
from typing import Any, Dict, List, Optional
from .hookspecs import hookspecs
from .registry import PluginRegistry, PluginInfo
from ..app_model.context import get_app_context
from ..app_model.actions import get_action_manager, Action


class PluginManager:
    """
    Manages plugin loading, unloading, and hook execution.
    """
    
    def __init__(self):
        self._pm = pluggy.PluginManager("t_gui")
        self._pm.add_hookspecs(hookspecs)
        self._registry = PluginRegistry()
        self._loaded_plugins: Dict[str, Any] = {}
        self._context = get_app_context()
        self._action_manager = get_action_manager()
    
    @property
    def registry(self) -> PluginRegistry:
        """Get the plugin registry."""
        return self._registry
    
    def discover_plugins(self):
        """Discover plugins in registered paths."""
        self._registry.discover_plugins()
        self._context.emit('plugins_discovered')
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin by name.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to load.
            
        Returns
        -------
        bool
            True if plugin was loaded successfully.
        """
        if plugin_name in self._loaded_plugins:
            return True
        
        plugin_info = self._registry.get_plugin(plugin_name)
        if not plugin_info or not plugin_info.enabled:
            return False
        
        try:
            # Load the plugin module
            module = self._registry.load_plugin_module(plugin_name)
            if not module:
                return False
            
            # Register the plugin with pluggy
            self._pm.register(module, name=plugin_name)
            self._loaded_plugins[plugin_name] = module
            
            # Call setup hook
            self._pm.hook.t_gui_setup_plugin(plugin_manager=self)
            
            # Process plugin contributions
            self._process_plugin_contributions(plugin_name)
            
            self._context.emit('plugin_loaded', plugin_name=plugin_name)
            return True
            
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin by name.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to unload.
            
        Returns
        -------
        bool
            True if plugin was unloaded successfully.
        """
        if plugin_name not in self._loaded_plugins:
            return True
        
        try:
            # Call teardown hook
            self._pm.hook.t_gui_teardown_plugin(plugin_manager=self)
            
            # Unregister from pluggy
            plugin = self._loaded_plugins[plugin_name]
            self._pm.unregister(plugin, name=plugin_name)
            del self._loaded_plugins[plugin_name]
            
            self._context.emit('plugin_unloaded', plugin_name=plugin_name)
            return True
            
        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self):
        """Load all enabled plugins."""
        for plugin_info in self._registry.get_enabled_plugins():
            self.load_plugin(plugin_info.name)
    
    def unload_all_plugins(self):
        """Unload all loaded plugins."""
        for plugin_name in list(self._loaded_plugins.keys()):
            self.unload_plugin(plugin_name)
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to reload.
            
        Returns
        -------
        bool
            True if plugin was reloaded successfully.
        """
        self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name)
    
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """
        Check if a plugin is loaded.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to check.
            
        Returns
        -------
        bool
            True if the plugin is loaded.
        """
        return plugin_name in self._loaded_plugins
    
    def get_loaded_plugins(self) -> List[str]:
        """
        Get list of loaded plugin names.
        
        Returns
        -------
        List[str]
            List of loaded plugin names.
        """
        return list(self._loaded_plugins.keys())
    
    def _process_plugin_contributions(self, plugin_name: str):
        """Process contributions from a loaded plugin."""
        try:
            # Process action contributions
            action_contributions = self._pm.hook.t_gui_get_action_contributions()
            for contributions in action_contributions:
                if contributions:
                    for action_data in contributions:
                        action = Action(
                            id=action_data['id'],
                            title=action_data['title'],
                            callback=action_data['callback'],
                            tooltip=action_data.get('tooltip'),
                            icon=action_data.get('icon'),
                            shortcut=action_data.get('shortcut'),
                            enabled=action_data.get('enabled', True)
                        )
                        self._action_manager.register_action(action)
            
            # Process widget contributions
            widget_contributions = self._pm.hook.t_gui_get_widget_contributions()
            for contributions in widget_contributions:
                if contributions:
                    self._context.emit('widget_contributions', 
                                     plugin_name=plugin_name, 
                                     contributions=contributions)
            
            # Process menu contributions
            menu_contributions = self._pm.hook.t_gui_get_menu_contributions()
            for contributions in menu_contributions:
                if contributions:
                    self._context.emit('menu_contributions',
                                     plugin_name=plugin_name,
                                     contributions=contributions)
            
            # Process reader contributions
            reader_contributions = self._pm.hook.t_gui_get_reader_contributions()
            for contributions in reader_contributions:
                if contributions:
                    self._context.emit('reader_contributions',
                                     plugin_name=plugin_name,
                                     contributions=contributions)
            
            # Process writer contributions
            writer_contributions = self._pm.hook.t_gui_get_writer_contributions()
            for contributions in writer_contributions:
                if contributions:
                    self._context.emit('writer_contributions',
                                     plugin_name=plugin_name,
                                     contributions=contributions)
                                     
        except Exception as e:
            print(f"Error processing contributions for plugin {plugin_name}: {e}")


# Global plugin manager instance
_global_plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager."""
    return _global_plugin_manager
