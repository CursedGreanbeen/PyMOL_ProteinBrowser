from pymol import cmd

from ..core.browser import browse as core_browse
from ..utils.pymol_utils import get_browser
from ..utils.config import config
from ..utils.fasta_handler import read_fasta_file


def _browse_next():
    get_browser().next()

def _browse_previous():
    get_browser().previous()

def _browse_first():
    get_browser().first()

def _browse_load(n: int):
    get_browser().load(int(n))

def _browse_list():
    get_browser().list()

def _browse_color():
    get_browser().color_chains()


def _show_fasta(original: bool = False):
    """Показывает FASTA текущего объекта."""
    obj_name = get_browser().current_object
    
    if original:
        fasta_path = config.get_original_fasta_path(obj_name)
    else:
        fasta_path = config.get_fasta_path(obj_name)

    content = read_fasta_file(fasta_path)
    if content:
        print(content)
    else:
        print(f"[browser] FASTA-файл не найден: {fasta_path}")


def _show_browser_commands():
    """Показывает список команд браузера."""
    print("\n" + "="*60)
    print("Доступные команды browse_proteins:")
    print("="*60)
    print("  browse(folder_path)      - запустить браузер")
    print("  browse_next()            - следующая структура")
    print("  browse_prev()            - предыдущая структура")
    print("  browse_first()           - первая структура")
    print("  browse_load(n)           - загрузить структуру по номеру (1-indexed)")
    print("  browse_list()            - показать список всех структур")
    print("  browse_color()           - раскрасить цепи в разные цвета")
    print("  show_fasta()             - показать FASTA (fasta-filtered)")
    print("  show_fasta(True)         - показать оригинальный FASTA")
    print("="*60 + "\n")


def register_browser_commands():
    """Регистрирует все команды браузера в PyMOL."""
    cmd.extend("browse", core_browse)
    cmd.extend("browse_next", _browse_next)
    cmd.extend("browse_prev", _browse_previous)
    cmd.extend("browse_first", _browse_first)
    cmd.extend("browse_load", _browse_load)
    cmd.extend("browse_list", _browse_list)
    cmd.extend("browse_color", _browse_color)
    cmd.extend("show_fasta", _show_fasta)
    cmd.extend("show_browser_commands", _show_browser_commands)
