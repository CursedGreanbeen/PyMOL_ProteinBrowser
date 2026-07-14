# fasta_edit.py
# Скрипт для фильтрации FASTA на основе цепей в CIF файле

from pymol import cmd
from pathlib import Path
import sys
import builtins
import importlib.util

# Получаем путь к папке scripts
SCRIPTS_DIR = Path("/home/path")

# Загружаем config.py как модуль
config_path = SCRIPTS_DIR / "config.py"
spec = importlib.util.spec_from_file_location("config", str(config_path))
config_module = importlib.util.module_from_spec(spec)
sys.modules["config"] = config_module
spec.loader.exec_module(config_module)
config = config_module.config

# Загружаем utils/fasta_handler.py как модуль
fasta_handler_path = SCRIPTS_DIR / "utils" / "fasta_handler.py"
spec = importlib.util.spec_from_file_location("utils.fasta_handler", str(fasta_handler_path))
fasta_handler_module = importlib.util.module_from_spec(spec)
sys.modules["utils.fasta_handler"] = fasta_handler_module
spec.loader.exec_module(fasta_handler_module)

filter_original_fasta = fasta_handler_module.filter_original_fasta


def _get_browser():
    """
    Ищет экземпляр ProteinBrowser всеми доступными способами.
    """
    browser = getattr(builtins, '_protein_browser', None)
    if browser is not None:
        return browser

    for mod_name in list(sys.modules.keys()):
        if 'browse' in mod_name.lower():
            mod = sys.modules[mod_name]
            b = getattr(mod, '_browser', None)
            if b is not None:
                return b

    return None


def get_chains_from_current_obj():
    """
    Получает список цепей из текущего загруженного объекта в PyMOL.

    Returns:
        List[str]: Список идентификаторов цепей (например, ['A', 'B', 'F'])
    """
    _browser = _get_browser()

    if _browser is None:
        print("Ошибка: ProteinBrowser не найден")
        return None

    if not _browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        return None

    try:
        chains = cmd.get_chains(_browser.current_obj_name)
        return list(chains)
    except Exception as e:
        print(f"Ошибка получения цепей: {e}")
        return None


def fasta_modify():
    """
    Основная функция для фильтрации FASTA на основе цепей в текущем CIF объекте.

    Логика:
    1. Получаем текущий объект из ProteinBrowser
    2. Получаем цепи из текущего объекта
    3. Фильтрует оригинальный FASTA из fasta-sequences/
    4. Добавляет отфильтрованный контент в fasta-filtered/

    Пример использования:
        run /home/.../scripts/browse_proteins.py
        run /home/.../scripts/fasta_edit.py
        browse("/home/.../CIFs-filtered")
        browse_first()
        fasta_modify()
    """
    _browser = _get_browser()

    if _browser is None:
        print("Ошибка: ProteinBrowser не найден")
        print("Сначала загрузите browse_proteins.py и запустите browse()")
        return

    if not _browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        print("Загрузите структуру через browse_first(), browse_next() и т.д.")
        return

    current_obj = _browser.current_obj_name
    chains = get_chains_from_current_obj()

    if not chains:
        print("Не удалось получить цепи из объекта")
        return

    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")
    print(f"Цепи: {', '.join(chains)}")

    # Используем функцию из utils/fasta_handler.py
    if filter_original_fasta(current_obj, chains):
        print("FASTA успешно обновлён")
    else:
        print("Ошибка при обновлении FASTA")

    print(f"{'='*60}\n")


# Регистрируем команду в PyMOL
cmd.extend("fasta_modify", fasta_modify)

# Приветственное сообщение
print("\n" + "="*60)
print("fasta_edit.py загружен.")
print("Доступные команды:")
print("  fasta_modify()  - отфильтровать FASTA по цепям текущего объекта")
print("="*60 + "\n")
