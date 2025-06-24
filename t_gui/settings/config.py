"""
Configuration management for T-GUI.
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path
from ..events import EventEmitter


class Settings(EventEmitter):
    """
    Manages application settings and configuration.
    
    Settings are stored in JSON format and can be persisted to disk.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        super().__init__()
        
        # Determine config directory
        if config_dir is None:
            config_dir = self._get_default_config_dir()
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        
        # Default settings
        self._defaults = {
            'appearance': {
                'theme': 'dark',
                'font_size': 10,
                'font_family': 'Arial'
            },
            'viewer': {
                'background_color': '#2b2b2b',
                'default_colormap': 'gray',
                'interpolation': 'nearest'
            },
            'plugins': {
                'auto_discover': True,
                'auto_load': False,
                'plugin_dirs': []
            },
            'performance': {
                'max_layers': 100,
                'cache_size_mb': 512,
                'async_rendering': True
            }
        }
        
        self._settings: Dict[str, Any] = {}
        self._load_settings()
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 't_gui'
        else:  # Unix-like
            config_dir = Path.home() / '.config' / 't_gui'
        
        return config_dir
    
    def _load_settings(self):
        """Load settings from file."""
        # Start with defaults
        self._settings = self._deep_copy_dict(self._defaults)
        
        # Load from file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_settings = json.load(f)
                self._merge_settings(self._settings, file_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save settings
            with open(self.config_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _deep_copy_dict(self, d: Dict) -> Dict:
        """Deep copy a dictionary."""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_dict(value)
            else:
                result[key] = value
        return result
    
    def _merge_settings(self, target: Dict, source: Dict):
        """Merge source settings into target settings."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_settings(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Parameters
        ----------
        key : str
            Setting key in dot notation (e.g., 'appearance.theme').
        default : Any, optional
            Default value if key is not found.
            
        Returns
        -------
        Any
            The setting value.
        """
        keys = key.split('.')
        current = self._settings
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        Set a setting value.
        
        Parameters
        ----------
        key : str
            Setting key in dot notation (e.g., 'appearance.theme').
        value : Any
            Value to set.
        save : bool, optional
            Whether to save settings to file immediately. Default is True.
        """
        keys = key.split('.')
        current = self._settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        old_value = current.get(keys[-1])
        current[keys[-1]] = value
        
        # Emit change event
        self.emit('setting_changed', key=key, value=value, old_value=old_value)
        
        # Save if requested
        if save:
            self._save_settings()
    
    def has(self, key: str) -> bool:
        """
        Check if a setting key exists.
        
        Parameters
        ----------
        key : str
            Setting key in dot notation.
            
        Returns
        -------
        bool
            True if the key exists.
        """
        keys = key.split('.')
        current = self._settings
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False
        
        return True
    
    def remove(self, key: str, save: bool = True):
        """
        Remove a setting.
        
        Parameters
        ----------
        key : str
            Setting key in dot notation.
        save : bool, optional
            Whether to save settings to file immediately. Default is True.
        """
        keys = key.split('.')
        current = self._settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return  # Key doesn't exist
        
        # Remove the key
        if isinstance(current, dict) and keys[-1] in current:
            old_value = current.pop(keys[-1])
            self.emit('setting_removed', key=key, value=old_value)
            
            if save:
                self._save_settings()
    
    def reset_to_defaults(self, save: bool = True):
        """
        Reset all settings to defaults.
        
        Parameters
        ----------
        save : bool, optional
            Whether to save settings to file immediately. Default is True.
        """
        self._settings = self._deep_copy_dict(self._defaults)
        self.emit('settings_reset')
        
        if save:
            self._save_settings()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.
        
        Returns
        -------
        Dict[str, Any]
            All settings as a dictionary.
        """
        return self._deep_copy_dict(self._settings)
    
    def update(self, settings: Dict[str, Any], save: bool = True):
        """
        Update multiple settings at once.
        
        Parameters
        ----------
        settings : Dict[str, Any]
            Settings to update.
        save : bool, optional
            Whether to save settings to file immediately. Default is True.
        """
        self._merge_settings(self._settings, settings)
        self.emit('settings_updated', settings=settings)
        
        if save:
            self._save_settings()
    
    def save(self):
        """Save settings to file."""
        self._save_settings()


# Global settings instance
_global_settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return _global_settings
