"""
Ядро редактирования FASTA.

ТОЛЬКО бизнес-логика — без cmd.extend и регистрации.
"""
from pymol import cmd
import builtins

from ..utils.config import config
from ..utils.fasta_handler import filter_original_fasta


def _get_browser():
    """Ищет экземпляр ProteinBrowser."""
    browser = getattr(builtins, '_protein_browser', None)
    if browser is not None:
        return browser

    import sys
    for mod_name in list(sys.modules.keys()):
        if 'browser' in mod_name.lower():
            mod = sys.modules[mod_name]
            b = getattr(mod, '_browser_instance', None)
            if b is not None:
                return b

    return None


def get_chains_from_current_obj():
    """
    Получает список цепей из текущего загруженного объекта.

    Returns:
        list[str]: Список идентификаторов цепей или None
    """
    browser = _get_browser()

    if browser is None:
        print("Ошибка: ProteinBrowser не найден")
        return None

    if not browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        return None

    try:
        chains = cmd.get_chains(browser.current_obj_name)
        return list(chains)
    except Exception as e:
        print(f"Ошибка получения цепей: {e}")
        return None


def filter_fasta_for_current_object():
    """
    Фильтрует оригинальный FASTA на основе цепей в текущем CIF объекте.

    Возвращает:
        bool: True если успешно, False иначе
    """
    browser = _get_browser()

    if browser is None:
        print("Ошибка: ProteinBrowser не найден")
        return False

    if not browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        return False

    current_obj = browser.current_obj_name
    chains = get_chains_from_current_obj()

    if not chains:
        print("Не удалось получить цепи из объекта")
        return False

    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")
    print(f"Цепи: {', '.join(chains)}")

    if filter_original_fasta(current_obj, chains):
        print("FASTA успешно обновлён")
    else:
        print("Ошибка при обновлении FASTA")

    print(f"{'='*60}\n")
    return True
