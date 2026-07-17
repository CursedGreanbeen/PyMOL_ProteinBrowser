"""
Регистрация команд браузера в PyMOL.

ТОЛЬКО обёртки для cmd.extend — без бизнес-логики.
"""
from pymol import cmd

from ..core.browser import browse as core_browse, get_browser


def _browse_next():
    """Загружает следующую структуру"""
    browser = get_browser()
    if browser:
        browser.load_next()
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _browse_previous():
    """Загружает предыдущую структуру"""
    browser = get_browser()
    if browser:
        browser.load_previous()
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _browse_first():
    """Загружает первую структуру"""
    browser = get_browser()
    if browser:
        browser.load_first()
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _browse_load(index):
    """Загружает структуру по номеру (1-indexed)"""
    browser = get_browser()
    if browser:
        browser.load_specific(index - 1)
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _browse_list():
    """Показывает список всех структур"""
    browser = get_browser()
    if browser:
        browser.list_all()
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _browse_color():
    """Раскрашивает цепи текущей структуры"""
    browser = get_browser()
    if browser:
        browser.color_chains()
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _show_fasta(if_original=False):
    """
    Показывает содержимое FASTA-файла.

    Args:
        if_original: True для оригинального FASTA (fasta-sequences),
                    False для отфильтрованного (fasta-filtered, дефолт)
    """
    browser = get_browser()
    if not browser or not browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        print("Сначала загрузите структуру через browse_next(), browse_first() и т.д.")
        return

    from ..utils.config import config

    base_name = browser.current_obj_name.replace("_cropped", "")

    if if_original:
        folder = config.get_fasta_original_folder()
    else:
        folder = config.get_fasta_folder()

    fasta_path = folder / f"{base_name}.fasta"

    if not fasta_path.exists():
        folder_type = "оригинальный" if if_original else "отфильтрованный"
        print(f"Предупреждение: {folder_type} FASTA-файл не найден: {fasta_path}")
        return

    print(f"\n{'='*60}")
    print(f"{'Оригинальный ' if if_original else ''}FASTA-файл: {fasta_path}")
    print(f"{'='*60}\n")

    try:
        with open(fasta_path, 'r') as f:
            content = f.read()
        print(content)
    except Exception as e:
        print(f"Ошибка чтения FASTA: {e}")

    print(f"{'='*60}\n")
    return fasta_path


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
