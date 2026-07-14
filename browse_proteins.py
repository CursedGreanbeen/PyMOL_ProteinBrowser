# browse_proteins.py
# Скрипт для итеративного просмотра белковых структур по одной
from pymol import cmd
from pathlib import Path
import os
import sys
import glob
import builtins
import importlib.util

# Получаем путь к папке scripts и загружаем config через importlib
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


class ProteinBrowser:
    """Браузер белковых структур с возможностью переключения по одному"""

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_list = []
        self.current_index = -1
        self.current_obj_name = None

        # Собираем все файлы структур
        extensions = ['*.pdb', '*.pdb.gz', '*.cif', '*.cif.gz']
        for ext in extensions:
            self.file_list.extend(glob.glob(os.path.join(folder_path, ext)))

        # Сортируем по имени
        self.file_list.sort()

        if not self.file_list:
            print(f"Файлы не найдены в {folder_path}")
            return

        print(f"Найдено структур: {len(self.file_list)}")
        self._show_status()

    def _get_obj_name(self, filepath):
        """Генерирует имя объекта из имени файла"""
        filename = os.path.basename(filepath)
        obj_name = os.path.splitext(filename)[0]
        if obj_name.endswith('.gz'):
            obj_name = obj_name[:-3]
        return obj_name

    def _show_status(self):
        """Показывает текущий статус"""
        if self.current_index >= 0 and self.current_index < len(self.file_list):
            current_file = os.path.basename(self.file_list[self.current_index])
            print(f"\n{'='*50}")
            print(f"Текущая структура: {current_file}")
            print(f"Позиция: {self.current_index + 1}/{len(self.file_list)}")
            print(f"{'='*50}\n")
        else:
            print("Нет загруженной структуры")

    def load_first(self):
        """Загружает первую структуру"""
        if not self.file_list:
            print("Нет файлов для загрузки")
            return
        self.current_index = 0
        self._load_current()

    def load_next(self):
        """Загружает следующую структуру"""
        if not self.file_list:
            print("Нет файлов для загрузки")
            return
        if self.current_index < len(self.file_list) - 1:
            self.current_index += 1
            self._load_current()
        else:
            print("Это последняя структура")

    def load_previous(self):
        """Загружает предыдущую структуру"""
        if not self.file_list:
            print("Нет файлов для загрузки")
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._load_current()
        elif self.current_index == -1:
            self.current_index = 0
            self._load_current()
        else:
            print("Это первая структура")

    def load_specific(self, index):
        """Загружает структуру по индексу (начиная с 0)"""
        if not self.file_list:
            print("Нет файлов для загрузки")
            return
        if 0 <= index < len(self.file_list):
            self.current_index = index
            self._load_current()
        else:
            print(f"Некорректный индекс. Доступно: 0-{len(self.file_list)-1}")

    def _load_current(self):
        """Загружает текущую структуру"""
        filepath = self.file_list[self.current_index]
        obj_name = self._get_obj_name(filepath)

        # Удаляем все объекты и селекции перед загрузкой
        try:
            cmd.delete("all")
        except:
            pass

        # Загружаем новую
        try:
            cmd.load(filepath, obj_name)
            self.current_obj_name = obj_name
            self._show_status()
            # Автоматически раскрашиваем цепи
            self.color_chains()
        except Exception as e:
            print(f"Ошибка загрузки {filepath}: {e}")
            self.current_obj_name = None

    def get_current_info(self):
        """Возвращает информацию о текущей структуре"""
        if self.current_index >= 0 and self.current_index < len(self.file_list):
            return {
                'index': self.current_index,
                'total': len(self.file_list),
                'filename': os.path.basename(self.file_list[self.current_index]),
                'obj_name': self.current_obj_name
            }
        return None

    def list_all(self):
        """Показывает список всех структур"""
        print(f"\nВсего структур: {len(self.file_list)}\n")
        for i, filepath in enumerate(self.file_list, 1):
            filename = os.path.basename(filepath)
            print(f"{i:4d}. {filename}")
        print()

    def color_chains(self):
        """
        Раскрашивает каждую цепь структуры в свой цвет.
        Использует палитру из 24 цветов PyMOL.
        """
        if not self.current_obj_name:
            print("Нет загруженной структуры")
            return

        # Базовые цвета PyMOL + дополнительные
        colors = [
            'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'orange',
            'white', 'gray',
            'limon', 'lime', 'forest', 'deepblue', 'purple', 'violet',
            'pink', 'salmon', 'brown', 'wheat', 'sand'
        ]

        chains = cmd.get_chains(self.current_obj_name)

        if not chains:
            print(f"Цепи не найдены в {self.current_obj_name}")
            return

        print(f"Найдено цепей: {len(chains)}")

        for i, chain in enumerate(chains):
            color_name = colors[i % len(colors)]
            selection_name = f"{self.current_obj_name}_chain_{chain}"
            cmd.select(selection_name, f"({self.current_obj_name}) and chain {chain}")
            try:
                cmd.color(color_name, selection_name)
                print(f"  Цепь {chain}: {color_name}")
            except Exception as e:
                print(f"  Цепь {chain}: цвет '{color_name}' не поддерживается, используем 'red' ({e})")
                cmd.color('red', selection_name)

        print(f"\nРаскрашено цепей: {len(chains)}")
        cmd.deselect()


# Глобальный экземпляр браузера
_browser = None


def browse(folder_path):
    """
    Запускает браузер белковых структур

    Пример:
        browse("/path/to/folder")
    """
    global _browser
    _browser = ProteinBrowser(folder_path)

    # --- FIX: сохраняем _browser в builtins, чтобы cleanup_pipeline.py мог его найти ---
    builtins._protein_browser = _browser

    # Регистрируем команды
    cmd.extend("browse_next", browse_next)
    cmd.extend("browse_prev", browse_previous)
    cmd.extend("browse_first", browse_first)
    cmd.extend("browse_load", browse_load)
    cmd.extend("browse_list", browse_list)
    cmd.extend("browse_color", browse_color)
    cmd.extend("show_fasta", show_fasta)

    print("\nКоманды доступны:")
    print("  browse_next()        - следующая структура")
    print("  browse_prev()        - предыдущая структура")
    print("  browse_first()       - первая структура")
    print("  browse_load(n)       - загрузить структуру по номеру (1-indexed)")
    print("  browse_list()        - показать список всех структур")
    print("  browse_color()       - раскрасить цепи в разные цвета")
    print("  show_fasta()         - показать FASTA (fasta-filtered)")
    print("  show_fasta(True)     - показать оригинальный FASTA (fasta-sequences)")


def browse_next():
    """Загружает следующую структуру"""
    if _browser:
        _browser.load_next()
    else:
        print("Сначала вызовите browse('/path/to/folder')")

def browse_previous():
    """Загружает предыдущую структуру"""
    if _browser:
        _browser.load_previous()
    else:
        print("Сначала вызовите browse('/path/to/folder')")

def browse_first():
    """Загружает первую структуру"""
    if _browser:
        _browser.load_first()
    else:
        print("Сначала вызовите browse('/path/to/folder')")

def browse_load(index):
    """Загружает структуру по номеру (1-indexed)"""
    if _browser:
        _browser.load_specific(index - 1)
    else:
        print("Сначала вызовите browse('/path/to/folder')")

def browse_list():
    """Показывает список всех структур"""
    if _browser:
        _browser.list_all()
    else:
        print("Сначала вызовите browse('/path/to/folder')")

def browse_color():
    """Раскрашивает цепи текущей структуры"""
    if _browser:
        _browser.color_chains()
    else:
        print("Сначала вызовите browse('/path/to/folder')")


def _get_fasta_path(obj_name: str, if_original: bool = False) -> Path:
    """
    Возвращает путь к FASTA-файлу для объекта.

    Args:
        obj_name: Имя объекта (например, "8vul_cropped")
        if_original: True для оригинального FASTA, False для отфильтрованного

    Returns:
        Path к FASTA-файлу
    """
    base_name = obj_name.replace("_cropped", "")

    if if_original:
        folder = config.get_fasta_original_folder()
    else:
        folder = config.get_fasta_folder()

    return folder / f"{base_name}.fasta"


def show_fasta(if_original: bool = False):
    """
    Показывает содержимое FASTA-файла.

    Args:
        if_original: True для оригинального FASTA (fasta-sequences),
                    False для отфильтрованного (fasta-filtered, дефолт)

    Пример:
        Если текущий объект: 10fo_cropped
        show_fasta()         -> fasta-filtered/10fo.fasta
        show_fasta(True)     -> fasta-sequences/10fo.fasta
    """
    if not _browser or not _browser.current_obj_name:
        print("Ошибка: нет загруженной структуры")
        print("Сначала загрузите структуру через browse_next(), browse_first() и т.д.")
        return

    fasta_path = _get_fasta_path(_browser.current_obj_name, if_original=if_original)

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


def show_commands():
    """
    Показывает список доступных команд browse_proteins.

    Пример использования:
        run /home/.../scripts/browse_proteins.py
        show_commands()
    """
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
    print("  set_paths(...)           - установить кастомные пути")
    print("="*60 + "\n")


# Регистрируем команду show_commands
cmd.extend("show_commands", show_commands)


# set_paths уже доступна из config.py
cmd.extend("set_paths", set_paths)


# Пример использования в PyMOL:
# run /path/to/browse_proteins.py
# browse("/home/mullagaliamova/ClaudeWorkspace/PROJECTS/cdr-h3-folding/CIFs-filtered/")
# browse_next()
# browse_prev()
# browse_load(5)  # загрузить 5-ю структуру
#
# Установить кастомные пути на весь сеанс:
#   set_paths(fasta_folder="/home/.../fasta-filtered/2chains")
#
# Затем show_fasta() будет использовать этот путь автоматически:
#   show_fasta()  # откроет файл из fasta-filtered/2chains
