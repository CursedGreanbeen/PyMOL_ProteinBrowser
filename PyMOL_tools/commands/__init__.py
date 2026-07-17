"""Модуль регистрации команд PyMOL."""

from .browser_cmds import register_browser_commands
from .cleanup_cmds import register_cleanup_commands
from .fasta_cmds import register_fasta_edit_commands

__all__ = [
    'register_browser_commands',
    'register_cleanup_commands',
    'register_fasta_edit_commands',
]
