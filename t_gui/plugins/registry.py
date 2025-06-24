"""
Plugin registry for managing plugin metadata and discovery.
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PluginInfo:
    """
    Information about a plugin.
    
    Attributes
    ----------
    name : str
        Plugin name.
    version : str
        Plugin version.
    description : str
        Plugin description.
    author : str
        Plugin author.
    module_name : str
        Python module name.
    entry_point : str
        Entry point function name.
    enabled : bool
        Whether the plugin is enabled.
    """
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    module_name: str = ""
    entry_point: str = "setup_plugin"
    enabled: bool = True


class PluginRegistry:
    """
    Registry for managing plugin discovery and metadata.
    """
    
    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._plugin_paths: List[Path] = []
        self._loaded_modules: Dict[str, Any] = {}
    
    def add_plugin_path(self, path: Path):
        """
        Add a path to search for plugins.
        
        Parameters
        ----------
        path : Path
            Directory path to search for plugins.
        """
        if path not in self._plugin_paths:
            self._plugin_paths.append(path)
    
    def register_plugin(self, plugin_info: PluginInfo):
        """
        Register a plugin.
        
        Parameters
        ----------
        plugin_info : PluginInfo
            Plugin information.
        """
        self._plugins[plugin_info.name] = plugin_info
    
    def unregister_plugin(self, plugin_name: str):
        """
        Unregister a plugin.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to unregister.
        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
        if plugin_name in self._loaded_modules:
            del self._loaded_modules[plugin_name]
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get plugin information.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin.
            
        Returns
        -------
        PluginInfo or None
            Plugin information if found.
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """
        Get all registered plugins.
        
        Returns
        -------
        List[PluginInfo]
            List of all plugin information.
        """
        return list(self._plugins.values())
    
    def get_enabled_plugins(self) -> List[PluginInfo]:
        """
        Get all enabled plugins.
        
        Returns
        -------
        List[PluginInfo]
            List of enabled plugin information.
        """
        return [plugin for plugin in self._plugins.values() if plugin.enabled]
    
    def discover_plugins(self):
        """
        Discover plugins in the registered plugin paths.
        """
        for plugin_path in self._plugin_paths:
            if not plugin_path.exists():
                continue
                
            for item in plugin_path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    # Python package
                    self._discover_package_plugin(item)
                elif item.suffix == ".py" and item.name != "__init__.py":
                    # Python module
                    self._discover_module_plugin(item)
    
    def _discover_package_plugin(self, package_path: Path):
        """Discover a plugin from a Python package."""
        try:
            # Look for plugin metadata
            metadata_file = package_path / "plugin.json"
            if metadata_file.exists():
                import json
                with open(metadata_file) as f:
                    metadata = json.load(f)
                
                plugin_info = PluginInfo(
                    name=metadata.get("name", package_path.name),
                    version=metadata.get("version", "0.1.0"),
                    description=metadata.get("description", ""),
                    author=metadata.get("author", ""),
                    module_name=package_path.name,
                    entry_point=metadata.get("entry_point", "setup_plugin"),
                    enabled=metadata.get("enabled", True)
                )
                self.register_plugin(plugin_info)
            else:
                # Default plugin info
                plugin_info = PluginInfo(
                    name=package_path.name,
                    module_name=package_path.name
                )
                self.register_plugin(plugin_info)
                
        except Exception as e:
            print(f"Error discovering plugin {package_path}: {e}")
    
    def _discover_module_plugin(self, module_path: Path):
        """Discover a plugin from a Python module."""
        try:
            module_name = module_path.stem
            plugin_info = PluginInfo(
                name=module_name,
                module_name=module_name
            )
            self.register_plugin(plugin_info)
        except Exception as e:
            print(f"Error discovering plugin {module_path}: {e}")
    
    def load_plugin_module(self, plugin_name: str) -> Optional[Any]:
        """
        Load a plugin module.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to load.
            
        Returns
        -------
        module or None
            The loaded module if successful.
        """
        if plugin_name in self._loaded_modules:
            return self._loaded_modules[plugin_name]
        
        plugin_info = self.get_plugin(plugin_name)
        if not plugin_info:
            return None
        
        try:
            # Try to import the module
            module = importlib.import_module(plugin_info.module_name)
            self._loaded_modules[plugin_name] = module
            return module
        except ImportError as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return None
    
    def enable_plugin(self, plugin_name: str):
        """
        Enable a plugin.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to enable.
        """
        plugin_info = self.get_plugin(plugin_name)
        if plugin_info:
            plugin_info.enabled = True
    
    def disable_plugin(self, plugin_name: str):
        """
        Disable a plugin.
        
        Parameters
        ----------
        plugin_name : str
            Name of the plugin to disable.
        """
        plugin_info = self.get_plugin(plugin_name)
        if plugin_info:
            plugin_info.enabled = False
