"""
Конфигурация путей для скриптов PyMOL.

Все пути определяются автоматически относительно расположения скриптов,
без жестко заданных абсолютных путей.

Пример использования:
    from config import config
    print(config.get_cif_folder())
    config.set_paths(fasta_folder="/custom/path")
"""
from pathlib import Path
import importlib

# Базовая директория проекта                                                                                                 
BASE_DIR = Path("/home/path")                                              

# Дефолтные пути                                                                                                             
CIF_FOLDER = BASE_DIR / "CIFs-filtered"                                                                                      
CIF_ORIGINAL_FOLDER = BASE_DIR / "CIFs"                                                                                      
FASTA_FOLDER = BASE_DIR / "fasta-filtered"                                                                                   
FASTA_ORIGINAL_FOLDER = BASE_DIR / "fasta-sequences"


class Config:
    """
    Конфигурация путей с возможностью сессионных переопределений.

    Пример:
        from config import config
        print(config.get_cif_folder())                                                                                       
        config.set_paths(fasta_folder="/home/.../custom-folder")
    """

    def __init__(self):
        # Дефолтные пути                                                                                                     
        self.cif_folder = CIF_FOLDER                                                                                         
        self.cif_original_folder = CIF_ORIGINAL_FOLDER                                                                       
        self.fasta_folder = FASTA_FOLDER                                                                                     
        self.fasta_original_folder = FASTA_ORIGINAL_FOLDER

        # Сессионные переопределения
        self._session_cif_folder = None
        self._session_cif_original_folder = None
        self._session_fasta_folder = None
        self._session_fasta_original_folder = None

    def set_paths(
        self,
        cif_folder: str | None = None,
        cif_original_folder: str | None = None,
        fasta_folder: str | None = None,
        fasta_original_folder: str | None = None
    ):
        """
        Устанавливает пути на текущую сессию.

        Args:
            cif_folder: Путь к папке с CIF (отфильтрованные)
            cif_original_folder: Путь к папке с оригинальными CIF
            fasta_folder: Путь к папке с FASTA (отфильтрованные)
            fasta_original_folder: Путь к папке с оригинальными FASTA

        Пример:
            config.set_paths(fasta_folder="/home/user/custom-fasta")
            config.set_paths()  # сброс на дефолты
        """
        if cif_folder is not None:                                                                                          
            self._session_cif_folder = Path(cif_folder)                                                                     
        else:                                                                                                               
            self._session_cif_folder = None
        if cif_original_folder is not None:                                                                                 
            self._session_cif_original_folder = Path(cif_original_folder)                                                   
        else:                                                                                                               
            self._session_cif_original_folder = None                                                                        
                                                                                                                            
        if fasta_folder is not None:                                                                                        
            self._session_fasta_folder = Path(fasta_folder)                                                                 
        else:                                                                                                               
            self._session_fasta_folder = None                                                                               
                                                                                                                            
        if fasta_original_folder is not None:                                                                               
            self._session_fasta_original_folder = Path(fasta_original_folder)                                               
        else:                                                                                                               
            self._session_fasta_original_folder = None         

    def get_cif_folder(self) -> Path:
        """Возвращает путь к папке с отфильтрованными CIF"""
        return self._session_cif_folder or self.cif_folder

    def get_cif_original_folder(self) -> Path:
        """Возвращает путь к папке с оригинальными CIF"""
        return self._session_cif_original_folder or self.cif_original_folder

    def get_fasta_folder(self) -> Path:
        """Возвращает путь к папке с отфильтрованными FASTA"""
        return self._session_fasta_folder or self.fasta_folder

    def get_fasta_original_folder(self) -> Path:
        """Возвращает путь к папке с оригинальными FASTA"""
        return self._session_fasta_original_folder or self.fasta_original_folder

    def reset_paths(self):
        """Сбрасывает все сессионные переопределения"""
        self._session_cif_folder = None
        self._session_cif_original_folder = None
        self._session_fasta_folder = None
        self._session_fasta_original_folder = None

    def show_paths(self):
        """Показывает текущие пути"""
        print("\nТекущие пути конфигурации:")
        print(f"  Base dir: {self.base_dir}")
        print(f"  Scripts dir: {self.scripts_dir}")
        print(f"  CIF folder: {self.get_cif_folder()}")
        print(f"  CIF original folder: {self.get_cif_original_folder()}")
        print(f"  FASTA folder: {self.get_fasta_folder()}")
        print(f"  FASTA original folder: {self.get_fasta_original_folder()}")


# Глобальный экземпляр
config = Config()


# Функция-обёртка для удобства в PyMOL
def set_paths(
    cif_folder: str | None = None,
    cif_original_folder: str | None = None,
    fasta_folder: str | None = None,
    fasta_original_folder: str | None = None
):
    """
    Устанавливает пути на текущую сессию.

    Пример:
        set_paths(fasta_folder="/home/user/custom-fasta")
    """
    config.set_paths(cif_folder, cif_original_folder, fasta_folder, fasta_original_folder)                                  
    print("\nТекущие пути:")                                                                                                
    print(f"  CIF folder: {config.get_cif_folder()}")                                                                       
    print(f"  CIF original folder: {config.get_cif_original_folder()}")                                                     
    print(f"  FASTA folder: {config.get_fasta_folder()}")                                                                   
    print(f"  FASTA original folder: {config.get_fasta_original_folder()}") 
    config.show_paths()


# Приветственное сообщение при загрузке
print("\n" + "=" * 60)
print("config.py загружен. Пути определены автоматически.")
print(f"Base directory: {config.base_dir}")
print("=" * 60 + "\n")
