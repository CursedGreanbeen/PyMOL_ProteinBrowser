"""
Регистрация команд cleanup pipeline в PyMOL.

ТОЛЬКО обёртки для cmd.extend — без бизнес-логики.
"""
from pymol import cmd

from ..core.cleanup import (
    cleanup_selected_chains,
    remove_non_protein_components,
    crop_range,
)
from ..utils.config import config


def _show_cleanup_commands():
    """Показывает список команд cleanup"""
    print("\n" + "="*60)
    print("Доступные команды cleanup_pipeline:")
    print("="*60)
    print("  cleanup_selected()    - удалить выбранные цепи")
    print("  remove_non_protein()  - удалить всё, что не protein")
    print("  append_fasta(content) - добавить FASTA-записи")
    print("  crop_range()          - обрезать residues в selection")
    print("  set_paths(...)        - установить пути на сеанс")
    print("="*60 + "\n")


def _set_session_paths(
    cif_folder=None,
    cif_original_folder=None,
    fasta_folder=None,
    fasta_original_folder=None
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


def register_cleanup_commands():
    """Регистрирует все команды cleanup pipeline в PyMOL."""
    cmd.extend("cleanup_selected", cleanup_selected_chains)
    cmd.extend("remove_non_protein", remove_non_protein_components)
    cmd.extend("crop_range", crop_range)
    cmd.extend("set_paths", _set_session_paths)
    cmd.extend("show_cleanup_commands", _show_cleanup_commands)
