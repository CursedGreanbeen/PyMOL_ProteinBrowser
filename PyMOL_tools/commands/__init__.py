"""Модуль регистрации команд PyMOL."""

from .browser_cmds import register_browser_commands
from .cleanup_cmds import register_cleanup_commands
from .file_ops_cmds import register_file_ops_commands

__all__ = [
    'register_browser_commands',
    'register_cleanup_commands',
    'register_file_ops_commands',
]
