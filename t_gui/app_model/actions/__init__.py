"""
Action system for T-GUI.

This module defines the action system that allows for creating reusable
commands that can be triggered from menus, toolbars, or keyboard shortcuts.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from ..context import get_app_context


@dataclass
class Action:
    """
    Represents an action that can be executed.
    
    Attributes
    ----------
    id : str
        Unique identifier for the action.
    title : str
        Display title for the action.
    callback : Callable
        Function to execute when action is triggered.
    tooltip : str, optional
        Tooltip text for the action.
    icon : str, optional
        Icon identifier for the action.
    shortcut : str, optional
        Keyboard shortcut for the action.
    enabled : bool
        Whether the action is currently enabled.
    """
    id: str
    title: str
    callback: Callable
    tooltip: Optional[str] = None
    icon: Optional[str] = None
    shortcut: Optional[str] = None
    enabled: bool = True


class ActionManager:
    """
    Manages application actions.
    """
    
    def __init__(self):
        self._actions: Dict[str, Action] = {}
        self._context = get_app_context()
    
    def register_action(self, action: Action):
        """
        Register an action.
        
        Parameters
        ----------
        action : Action
            The action to register.
        """
        self._actions[action.id] = action
        self._context.emit('action_registered', action=action)
    
    def unregister_action(self, action_id: str):
        """
        Unregister an action.
        
        Parameters
        ----------
        action_id : str
            The ID of the action to unregister.
        """
        if action_id in self._actions:
            action = self._actions.pop(action_id)
            self._context.emit('action_unregistered', action=action)
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """
        Get an action by ID.
        
        Parameters
        ----------
        action_id : str
            The action ID.
            
        Returns
        -------
        Action or None
            The action if found, None otherwise.
        """
        return self._actions.get(action_id)
    
    def execute_action(self, action_id: str, *args, **kwargs):
        """
        Execute an action by ID.
        
        Parameters
        ----------
        action_id : str
            The action ID to execute.
        *args, **kwargs
            Arguments to pass to the action callback.
        """
        action = self.get_action(action_id)
        if action and action.enabled:
            try:
                action.callback(*args, **kwargs)
                self._context.emit('action_executed', action=action)
            except Exception as e:
                self._context.emit('action_error', action=action, error=e)
                raise
    
    def get_all_actions(self) -> List[Action]:
        """
        Get all registered actions.
        
        Returns
        -------
        List[Action]
            List of all actions.
        """
        return list(self._actions.values())
    
    def set_action_enabled(self, action_id: str, enabled: bool):
        """
        Enable or disable an action.
        
        Parameters
        ----------
        action_id : str
            The action ID.
        enabled : bool
            Whether to enable the action.
        """
        action = self.get_action(action_id)
        if action:
            action.enabled = enabled
            self._context.emit('action_enabled_changed', action=action, enabled=enabled)


# Global action manager instance
_global_action_manager = ActionManager()

def get_action_manager() -> ActionManager:
    """Get the global action manager."""
    return _global_action_manager


# Decorator for registering actions
def action(action_id: str, title: str, **kwargs):
    """
    Decorator for registering an action.
    
    Parameters
    ----------
    action_id : str
        Unique identifier for the action.
    title : str
        Display title for the action.
    **kwargs
        Additional action properties.
    """
    def decorator(func: Callable):
        action_obj = Action(
            id=action_id,
            title=title,
            callback=func,
            **kwargs
        )
        get_action_manager().register_action(action_obj)
        return func
    return decorator
