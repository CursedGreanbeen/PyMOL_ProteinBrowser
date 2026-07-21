"""
Ядро браузера белковых структур.

ТОЛЬКО бизнес-логика класса ProteinBrowser — без cmd.extend и регистрации.
"""
from pymol import cmd
from pathlib import Path
import os
import glob
import builtins

from ..utils.config import config
from ..utils.pymol_utils import set_browser


class ProteinBrowser:
    """Браузер белковых структур с возможностью переключения по одному"""

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_list = []
        self.current_index = -1
        self.current_obj_name = None

        extensions = ['*.pdb', '*.pdb.gz', '*.cif', '*.cif.gz']
        for ext in extensions:
            self.file_list.extend(glob.glob(os.path.join(folder_path, ext)))

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

        try:
            cmd.delete("all")
        except:
            pass

        try:
            cmd.load(filepath, obj_name)
            self.current_obj_name = obj_name
            self._show_status()
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
        """Раскрашивает каждую цепь структуры в свой цвет."""
        if not self.current_obj_name:
            print("Нет загруженной структуры")
            return

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


# Глобальный экземпляр браузера (для доступа из других модулей)
_browser_instance = None


def browse(folder_path="/home/mullagaliamova/ClaudeWorkspace/PROJECTS/cdr-h3-folding/CIFs-filtered"):
    """
    Запускает браузер белковых структур.

    Args:
        folder_path: Путь к папке с CIF/PDB файлами (по умолчанию: CIFs-filtered)
    """
    global _browser_instance
    _browser_instance = ProteinBrowser(folder_path)
    builtins._protein_browser = _browser_instance
    set_browser(_browser_instance)


def get_browser():
    """Возвращает текущий экземпляр ProteinBrowser или None."""
    return _browser_instance
