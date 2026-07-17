"""
PyMOL_tools — набор инструментов для работы с белковыми структурами в PyMOL.

Использование:
    run /home/.../scripts/PyMOL_tools

Это загрузит все команды и покажет приветственное сообщение.

Архитектура:
    - core/         : Бизнес-логика (без PyMOL cmd.extend)
    - commands/     : Регистрация команд в PyMOL (обёртки)
    - utils/        : Утилиты (config, fasta_handler)
    - __init__.py   : Точка входа (регистрация + приветствие)
"""

# Регистрируем все команды в PyMOL
from .commands import (
    register_browser_commands,
    register_cleanup_commands,
    register_fasta_edit_commands,
)

# Показываем приветствие
from .utils.welcome import show_welcome

# Вызываем регистрацию и приветствие при загрузке
register_browser_commands()
register_cleanup_commands()
register_fasta_edit_commands()
show_welcome()
