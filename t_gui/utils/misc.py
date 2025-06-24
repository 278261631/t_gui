"""
Miscellaneous utility functions.
"""

import importlib
import sys
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def ensure_list(obj: Any) -> List[Any]:
    """
    Ensure an object is a list.
    
    Parameters
    ----------
    obj : Any
        Object to convert to list.
        
    Returns
    -------
    List[Any]
        The object as a list.
    """
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    elif isinstance(obj, (tuple, set)):
        return list(obj)
    else:
        return [obj]


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Parameters
    ----------
    dict1 : Dict
        First dictionary.
    dict2 : Dict
        Second dictionary (takes precedence).
        
    Returns
    -------
    Dict
        Merged dictionary.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_import(module_name: str, attribute: Optional[str] = None) -> Optional[Any]:
    """
    Safely import a module or attribute.
    
    Parameters
    ----------
    module_name : str
        Name of the module to import.
    attribute : str, optional
        Attribute to get from the module.
        
    Returns
    -------
    Any or None
        The imported module/attribute, or None if import failed.
    """
    try:
        module = importlib.import_module(module_name)
        if attribute:
            return getattr(module, attribute, None)
        return module
    except ImportError:
        return None


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the file extension from a path.
    
    Parameters
    ----------
    file_path : str or Path
        Path to the file.
        
    Returns
    -------
    str
        File extension (without the dot).
    """
    path = Path(file_path)
    return path.suffix.lstrip('.')


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Parameters
    ----------
    size_bytes : int
        Size in bytes.
        
    Returns
    -------
    str
        Formatted size string.
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max.
    
    Parameters
    ----------
    value : float
        Value to clamp.
    min_value : float
        Minimum value.
    max_value : float
        Maximum value.
        
    Returns
    -------
    float
        Clamped value.
    """
    return max(min_value, min(value, max_value))


def is_sequence(obj: Any) -> bool:
    """
    Check if an object is a sequence (but not string).
    
    Parameters
    ----------
    obj : Any
        Object to check.
        
    Returns
    -------
    bool
        True if object is a sequence.
    """
    try:
        iter(obj)
        return not isinstance(obj, (str, bytes))
    except TypeError:
        return False


def get_class_name(obj: Any) -> str:
    """
    Get the class name of an object.
    
    Parameters
    ----------
    obj : Any
        Object to get class name for.
        
    Returns
    -------
    str
        Class name.
    """
    return obj.__class__.__name__


def validate_color(color: Any) -> bool:
    """
    Validate if a color specification is valid.
    
    Parameters
    ----------
    color : Any
        Color to validate.
        
    Returns
    -------
    bool
        True if color is valid.
    """
    if isinstance(color, str):
        # Check hex color
        if color.startswith('#') and len(color) in [4, 7]:
            try:
                int(color[1:], 16)
                return True
            except ValueError:
                return False
        
        # Check named colors (simplified)
        named_colors = {
            'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'black', 'white', 'gray', 'grey', 'orange', 'purple'
        }
        return color.lower() in named_colors
    
    elif isinstance(color, (list, tuple)):
        # Check RGB/RGBA
        if len(color) in [3, 4]:
            return all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color)
    
    return False
