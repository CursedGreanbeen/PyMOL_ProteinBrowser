"""
Конфигурация путей для PyMOL_tools.

ТОЛЬКО конфигурация — без приветственных сообщений и регистрации команд.
"""
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path("/home/mullagaliamova/ClaudeWorkspace/PROJECTS/cdr-h3-folding/scripts/PyMOL_ProteinBrowser")

# Дефолтные пути (относительно проекта, а не PyMOL_ProteinBrowser)
PROJECT_ROOT = Path("/home/mullagaliamova/ClaudeWorkspace/PROJECTS/cdr-h3-folding")
CIF_FOLDER = PROJECT_ROOT / "CIFs-filtered"
CIF_ORIGINAL_FOLDER = PROJECT_ROOT / "CIFs"
FASTA_FOLDER = PROJECT_ROOT / "fasta-filtered"
FASTA_ORIGINAL_FOLDER = PROJECT_ROOT / "fasta-sequences"


class Config:
    """
    Конфигурация путей с возможностью сессионных переопределений.
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
    
    def get_cif_path(self, obj_name: str) -> Path:
        return self.get_cif_folder() / f"{obj_name}.cif"
    
    def get_fasta_path(self, obj_name: str) -> Path:
        return self.get_fasta_folder() / f"{obj_name}.fasta"
    
    def get_original_cif_path(self, obj_name: str) -> Path:
        return self.get_cif_original_folder() / f"{obj_name}.cif"
    
    def get_original_fasta_path(self, obj_name: str) -> Path:
        return self.get_fasta_original_folder() / f"{obj_name}.fasta"


# Глобальный экземпляр
config = Config()
