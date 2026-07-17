"""
Регистрация команд редактирования FASTA в PyMOL.

ТОЛЬКО обёртки для cmd.extend — без бизнес-логики.
"""
from pymol import cmd

from ..core.fasta_edit import (
    get_chains_from_current_obj,
    filter_fasta_for_current_object,
)


def register_fasta_edit_commands():
    """Регистрирует все команды редактирования FASTA в PyMOL."""
    cmd.extend("fasta_modify", filter_fasta_for_current_object)
    cmd.extend("get_chains", get_chains_from_current_obj)
