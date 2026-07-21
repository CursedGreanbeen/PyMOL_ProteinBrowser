"""
Алиас для загрузки PyMOL_tools.

Использование:
    run /home/.../scripts/PyMOL_ProteinBrowser/PyMOL_tools.py
"""
import sys
import importlib.util
from pathlib import Path

# Получаем путь к папке PyMOL_ProteinBrowser
SCRIPTS_DIR = Path("/home/mullagaliamova/ClaudeWorkspace/PROJECTS/cdr-h3-folding/scripts/PyMOL_ProteinBrowser")

# Загружаем PyMOL_tools/__init__.py как модуль
init_path = SCRIPTS_DIR / "PyMOL_tools" / "__init__.py"
spec = importlib.util.spec_from_file_location("PyMOL_tools", str(init_path))
pymol_tools_module = importlib.util.module_from_spec(spec)
sys.modules["PyMOL_tools"] = pymol_tools_module
spec.loader.exec_module(pymol_tools_module)

# Команды уже зарегистрированы через cmd.extend(), теперь экспортируем их
# в глобальную область видимости для доступа из PyMOL командной строки

# Импортируем функции напрямую из модулей
from PyMOL_tools.core.browser import browse
from PyMOL_tools.utils.pymol_utils import get_browser
from PyMOL_tools.core.cleanup import (
    cleanup_selected_chains as cleanup_selected,
    remove_non_protein_components as remove_non_protein,
    crop_range as crop_range,
)
from PyMOL_tools.core.file_ops import (
    revert_to_original as revert,
    append_fasta_sequences as append_fasta,
)
from PyMOL_tools.commands.cleanup_cmds import (
    _set_session_paths as set_paths,
    _show_cleanup_commands as show_cleanup_commands,
)
from PyMOL_tools.commands.browser_cmds import (
    _browse_next as browse_next,
    _browse_previous as browse_prev,
    _browse_first as browse_first,
    _browse_spec as browse_spec,
    _browse_list as browse_list,
    _browse_color as browse_color,
    _show_fasta as show_fasta,
    _show_browser_commands as show_browser_commands,
)

# Делаем доступными в глобальной области видимости
globals()['browse'] = browse
globals()['get_browser'] = get_browser
globals()['browse_next'] = browse_next
globals()['browse_prev'] = browse_prev
globals()['browse_first'] = browse_first
globals()['browse_spec'] = browse_spec
globals()['browse_list'] = browse_list
globals()['browse_color'] = browse_color
globals()['show_fasta'] = show_fasta
globals()['cleanup_selected'] = cleanup_selected
globals()['remove_non_protein'] = remove_non_protein
globals()['crop_range'] = crop_range
globals()['revert'] = revert
globals()['append_fasta'] = append_fasta
globals()['set_paths'] = set_paths
globals()['show_cleanup_commands'] = show_cleanup_commands
globals()['show_browser_commands'] = show_browser_commands
