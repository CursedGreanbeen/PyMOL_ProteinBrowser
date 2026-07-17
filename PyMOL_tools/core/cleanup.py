"""
Ядро cleanup pipeline.

ТОЛЬКО бизнес-логика очистки — без cmd.extend и регистрации.
"""
from pymol import cmd
import builtins
import re

from ..utils.config import config
from ..utils.fasta_handler import remove_chains_from_fasta, append_fasta_content, update_fasta_sequences


def _get_browser():
    """
    Ищет экземпляр ProteinBrowser всеми доступными способами.
    """
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


def cleanup_selected_chains():
    """
    Удаляет выбранные цепи из текущей структуры и соответствующего FASTA-файла.

    Возвращает:
        bool: True если успешно, False иначе
    """
    browser = _get_browser()

    if not browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        return False

    current_obj = browser.current_obj_name
    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")

    try:
        chains_in_selection = cmd.get_chains("sele")
    except Exception as e:
        print(f"Ошибка получения selection: {e}")
        return False

    if not chains_in_selection:
        print("Предупреждение: в selection нет цепей")
        print("Выделите нужные цепи в PyMOL перед запуском")
        return False

    print(f"Цепи в selection: {', '.join(chains_in_selection)}")

    cif_folder = config.get_cif_folder()
    fasta_folder = config.get_fasta_folder()

    cif_path = cif_folder / f"{current_obj}.cif"

    if not cif_path.exists():
        print(f"Предупреждение: CIF-файл не найден: {cif_path}")
    else:
        for chain in chains_in_selection:
            remove_cmd = f"remove ({current_obj}) and chain {chain}"
            cmd.do(remove_cmd)
            print(f"Удалена цепь {chain} из объекта")

        try:
            cmd.save(str(cif_path), current_obj)
            print(f"Сохранён CIF: {cif_path}")
        except Exception as e:
            print(f"Ошибка сохранения CIF: {e}")

    base_name = current_obj.replace("_cropped", "")
    fasta_path = fasta_folder / f"{base_name}.fasta"

    if not fasta_path.exists():
        print(f"Предупреждение: FASTA-файл не найден: {fasta_path}")
    else:
        if remove_chains_from_fasta(fasta_path, chains_in_selection):
            print(f"FASTA изменён: {fasta_path}")
        else:
            print("FASTA не изменён (цепи не найдены в заголовках)")

    print(f"{'='*60}\n")
    return True


def crop_range():
    browser = _get_browser()

    if not browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        return False

    current_obj = browser.current_obj_name
    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")

    try:
        chains_in_selection = cmd.get_chains("sele")
    except Exception as e:
        print(f"Ошибка получения selection: {e}")
        return False

    if not chains_in_selection:
        print("Предупреждение: в selection нет цепей")
        print("Выделите нужные цепи в PyMOL перед запуском")
        return False

    print(f"Цепи в selection: {', '.join(chains_in_selection)}")
    cmd.remove(f"{current_obj} and sele")

    chain_sequences = {}
    for chain in chains_in_selection:
        fasta_str = cmd.get_fastastr(f"{current_obj} and chain {chain}")
        # get_fastastr возвращает заголовок + последовательность
        fasta_lines = fasta_str.strip().split('\n')
        # Пропускаем первую строку (заголовок >...) и объединяем остальные
        sequence = ''.join(fasta_lines[1:])
        chain_sequences[chain] = sequence
        print(f"    --- Chain {chain} ---")
        print(sequence)


    cif_folder = config.get_cif_folder()
    fasta_folder = config.get_fasta_folder()
    cif_path = cif_folder / f"{current_obj}.cif"

    if not cif_path.exists():
        print(f"Предупреждение: CIF-файл не найден: {cif_path}")
    else:
        try:
            cmd.save(str(cif_path), current_obj)
            print(f"Сохранён CIF: {cif_path}")
        except Exception as e:
            print(f"Ошибка сохранения CIF: {e}")

    base_name = current_obj.replace("_cropped", "")
    fasta_path = fasta_folder / f"{base_name}.fasta"

    if not fasta_path.exists():
        print(f"Ошибка: FASTA-файл не найден: {fasta_path}")
    else:
        if update_fasta_sequences(fasta_path, chain_sequences):
            print(f"FASTA изменён: {fasta_path}")
        else:
            print("FASTA не изменён")

    print(f"{'='*60}\n")
    return True


def remove_non_protein_components():
    """
    Удаляет все объекты, которые не являются полимером-белком.

    Возвращает:
        bool: True если успешно, False иначе
    """
    print("\n" + "="*60)
    print("Удаление не-белковых компонентов...")
    print("Selection: not polymer.protein")

    browser = _get_browser()
    current_obj = browser.current_obj_name if browser else None

    cif_folder = config.get_cif_folder()

    try:
        cmd.remove("not polymer.protein")
        print("Удалены: вода, лиганды, ионы, нуклеиновые кислоты.")

        if current_obj:
            cif_path = cif_folder / f"{current_obj}.cif"
            try:
                cmd.save(str(cif_path), current_obj)
                print(f"Сохранён CIF: {cif_path}")
            except Exception as e:
                print(f"Ошибка сохранения CIF: {e}")
        else:
            print("Предупреждение: нет загруженной структуры для сохранения")
    except Exception as e:
        print(f"Ошибка: {e}")

    print("="*60 + "\n")
    return True


def append_fasta_sequences(fasta_content):
    """
    Добавляет FASTA-записи в соответствующий FASTA-файл.

    Args:
        fasta_content: Одна или несколько FASTA-записей в виде строки.

    Возвращает:
        bool: True если записи были добавлены, False иначе
    """
    browser = _get_browser()

    if browser is None:
        print("Ошибка: ProteinBrowser не найден")
        return False

    if not browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        return False

    current_obj = browser.current_obj_name
    base_name = current_obj.replace("_cropped", "")
    fasta_folder = config.get_fasta_folder()
    target_file = fasta_folder / f"{base_name}.fasta"

    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")
    print(f"Целевой FASTA-файл: {target_file}")

    if not target_file.exists():
        print(f"Ошибка: FASTA-файл не найден: {target_file}")
        print(f"{'='*60}\n")
        return False

    if isinstance(fasta_content, str):
        content = fasta_content.strip()
    else:
        content = "\n".join(fasta_content).strip()

    if not content:
        print("Предупреждение: пустой FASTA контент")
        return False

    if append_fasta_content(target_file, content):
        print(f"FASTA сохранён: {target_file}")
    else:
        print("Все записи уже существуют, файл не изменён")

    print(f"{'='*60}\n")
    return True
