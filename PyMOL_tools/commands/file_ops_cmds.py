from pymol import cmd
from ..core.file_ops import revert_to_original, append_fasta_sequences


def register_file_ops_commands():
    """Регистрирует команды работы с файлами в PyMOL."""
    cmd.extend("revert_to_original", revert_to_original)
    cmd.extend("append_fasta", append_fasta_sequences)
