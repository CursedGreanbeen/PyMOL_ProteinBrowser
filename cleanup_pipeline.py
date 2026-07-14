# cleanup_pipeline.py
# Скрипт для удаления цепей из CIF и FASTA файлов на основе PyMOL selection
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
set_paths = config_module.set_paths

# Загружаем utils/fasta_handler.py как модуль
fasta_handler_path = SCRIPTS_DIR / "utils" / "fasta_handler.py"
spec = importlib.util.spec_from_file_location("fasta_handler", str(fasta_handler_path))
fasta_handler_module = importlib.util.module_from_spec(spec)
sys.modules["utils.fasta_handler"] = fasta_handler_module
spec.loader.exec_module(fasta_handler_module)

remove_chains_from_fasta = fasta_handler_module.remove_chains_from_fasta
append_fasta_content = fasta_handler_module.append_fasta_content


def _get_browser():
    """
    Ищет экземпляр ProteinBrowser всеми доступными способами.

    Порядок поиска:
    1. builtins._protein_browser  — самый надёжный канал между двумя run-скриптами
    2. sys.modules — на случай если browse_proteins был загружен через import
    """
    # 1. Через builtins (browse_proteins.py записывает сюда при вызове browse())
    browser = getattr(builtins, '_protein_browser', None)
    if browser is not None:
        return browser

    # 2. Через sys.modules (работает если скрипт загружен через import, а не run)
    for mod_name in list(sys.modules.keys()):
        if 'browse' in mod_name.lower():
            mod = sys.modules[mod_name]
            b = getattr(mod, '_browser', None)
            if b is not None:
                return b

    return None


def cleanup_selected():
    """
    Удаляет выбранные цепи из текущей структуры и соответствующего FASTA-файла.

    Пример использования в PyMOL:
        run /home/.../scripts/browse_proteins.py
        run /home/.../scripts/cleanup_pipeline.py
        browse("/home/.../CIFs-filtered")
        browse_first()
        # Выделите нужные цепи в PyMOL, затем:
        cleanup_selected()
    """
    # Шаг 0: Получаем браузер
    _browser = _get_browser()

    if _browser is None:
        print("Ошибка: ProteinBrowser не найден")
        print("Сначала загрузите browse_proteins.py и запустите browse()")
        print("  run /home/.../scripts/browse_proteins.py")
        print("  browse(\"/home/.../CIFs-filtered\")")
        return

    # Шаг 1: Получаем текущий объект
    if not _browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        print("Загрузите структуру через browse_first(), browse_next() и т.д.")
        return

    current_obj = _browser.current_obj_name
    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")

    # Шаг 2: Получаем цепи из selection
    try:
        chains_in_selection = cmd.get_chains("sele")
    except Exception as e:
        print(f"Ошибка получения selection: {e}")
        return

    if not chains_in_selection:
        print("Предупреждение: в selection нет цепей")
        print("Выделите нужные цепи в PyMOL перед запуском")
        return

    print(f"Цепи в selection: {', '.join(chains_in_selection)}")

    # Получаем пути из config
    cif_folder = config.get_cif_folder()
    fasta_folder = config.get_fasta_folder()

    # Шаг 3: Сохраняем CIF без выбранных цепей
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

    # Шаг 4: Редактируем FASTA-файл (убираем _cropped из имени)
    base_name = current_obj.replace("_cropped", "")
    fasta_path = fasta_folder / f"{base_name}.fasta"

    if not fasta_path.exists():
        print(f"Предупреждение: FASTA-файл не найден: {fasta_path} (ищем по базовому имени {base_name})")
    else:
        if remove_chains_from_fasta(fasta_path, chains_in_selection):
            print(f"FASTA изменён: {fasta_path}")
        else:
            print("FASTA не изменён (цепи не найдены в заголовках)")

    print(f"{'='*60}\n")


# Регистрируем команду в PyMOL
def remove_non_protein():
    """
    Удаляет все объекты, которые не являются полимером-белком, и сохраняет CIF.

    Использует PyMOL selection 'not polymer.protein' для удаления:
    - Воды (HOH, WAT и т.д.)
    - Лигандов и кофакторов
    - Нуклеиновых кислот
    - Ионов и других малых молекул

    После удаления автоматически сохраняет CIF-файл.

    Пример использования:
        run /home/.../scripts/cleanup_pipeline.py
        remove_non_protein()
    """
    print("\n" + "="*60)
    print("Удаление не-белковых компонентов...")
    print("Selection: not polymer.protein")

    # Получаем текущий объект из ProteinBrowser
    _browser = _get_browser()
    current_obj = _browser.current_obj_name if _browser else None

    # Получаем путь из config
    cif_folder = config.get_cif_folder()

    try:
        cmd.remove("not polymer.protein")
        print("Удалены: вода, лиганды, ионы, нуклеиновые кислоты.")

        # Сохраняем CIF, если есть текущий объект
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


def append_fasta(fasta_content):
    """
    Добавляет FASTA-записи в соответствующий FASTA-файл в fasta-filtered.

    Args:
        fasta_content: Одна или несколько FASTA-записей в виде строки.

    Файл определяется по текущему загруженному объекту в ProteinBrowser.
    Проверяет на дубликаты по полному заголовку.

    Пример использования:
        browse_first()
        append_fasta(">10FO_5|Chain G|Heavy chain\\nEVQLQQSGAELVK...")
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
    base_name = current_obj.replace("_cropped", "")
    fasta_folder = config.get_fasta_folder()
    target_file = fasta_folder / f"{base_name}.fasta"

    print(f"\n{'='*60}")
    print(f"Текущий объект: {current_obj}")
    print(f"Целевой FASTA-файл: {target_file}")

    if not target_file.exists():
        print(f"Ошибка: FASTA-файл не найден: {target_file}")
        print(f"{'='*60}\n")
        return

    if isinstance(fasta_content, str):
        content = fasta_content.strip()
    else:
        content = "\n".join(fasta_content).strip()

    if not content:
        print("Предупреждение: пустой FASTA контент")
        return

    if append_fasta_content(target_file, content):
        print(f"FASTA сохранён: {target_file}")
    else:
        print("Все записи уже существуют, файл не изменён")

    print(f"{'='*60}\n")


def show_commands():
    """
    Показывает список доступных команд cleanup_pipeline.

    Пример использования:
        run /home/.../scripts/cleanup_pipeline.py
        show_commands()
    """
    print("\n" + "="*60)
    print("Доступные команды cleanup_pipeline:")
    print("="*60)
    print("  cleanup_selected()   - удалить выбранные цепи")
    print("  remove_non_protein() - удалить всё, что не protein")
    print("  append_fasta(content) - добавить FASTA-записи")
    print("  set_paths(...)       - установить пути на сеанс")
    print("  show_commands()      - показать это сообщение")
    print("="*60 + "\n")


# set_paths из config.py уже доступна, регистрируем её:
cmd.extend("set_paths", set_paths)


# Регистрируем команды в PyMOL
cmd.extend("cleanup_selected", cleanup_selected)
cmd.extend("remove_non_protein", remove_non_protein)
cmd.extend("append_fasta", append_fasta)
cmd.extend("show_commands", show_commands)


# Приветственное сообщение при загрузке
print("\n" + "="*60)
print("cleanup_pipeline.py загружен. Доступные команды:")
print("  cleanup_selected()   - удалить выбранные цепи из CIF и FASTA")
print("  remove_non_protein() - удалить всё, что не polymer.protein")
print("  append_fasta()       - добавить FASTA-записи в текущий файл")
print("  set_paths()          - установить пути на сеанс")
print("  show_commands()      - показать список команд")
print("="*60 + "\n")


# Пример использования в PyMOL:
# run /home/.../scripts/browse_proteins.py
# run /home/.../scripts/cleanup_pipeline.py
# browse("/home/.../CIFs-filtered")
# browse_first()
# # Выделите цепи в PyMOL, затем:
# cleanup_selected()
