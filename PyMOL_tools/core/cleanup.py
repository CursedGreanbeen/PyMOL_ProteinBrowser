from pymol import cmd
from ..utils.pymol_utils import get_current_object, get_selected_chains, _get_sequence_from_pymol, save_cif
from ..utils.fasta_handler import read_fasta_file, write_fasta_file, parse_fasta, serialize_fasta, remove_chain, update_sequence
from ..utils.config import config


def _run_cleanup_pipeline(delete_fn: callable, fasta_fn: callable) -> None:
    """
    Общий pipeline для операций очистки/обрезки.
    delete_fn — выполняет операцию в PyMOL.
    fasta_fn  — принимает dict[str, FastaRecord], возвращает обновлённый dict.
    """
    obj_name = get_current_object()
    chains = get_selected_chains()

    delete_fn(chains)

    cif_path = config.get_cif_path(obj_name)
    save_cif(obj_name, cif_path)

    fasta_path = config.get_fasta_path(obj_name)
    records = parse_fasta(read_fasta_file(fasta_path))
    updated = fasta_fn(records, chains)
    write_fasta_file(fasta_path, serialize_fasta(updated))


def cleanup_selected_chains() -> None:
    """Удаляет выбранные цепи из объекта и обновляет CIF/FASTA."""
    def delete_fn(chains: list[str]) -> None:
        cmd.remove("sele")

    def fasta_fn(records, chains):
        for chain in chains:
            remove_chain(records, chain)
        return records

    _run_cleanup_pipeline(delete_fn, fasta_fn)


def remove_non_protein_components() -> None:
    """Удаляет все не-белковые компоненты из объекта и обновляет CIF/FASTA."""
    def delete_fn(chains: list[str]) -> None:
        cmd.remove(f"{get_current_object()} and not polymer.protein")

    def fasta_fn(records, chains):
        return records  # FASTA содержит только белковые цепи — ничего не меняем

    _run_cleanup_pipeline(delete_fn, fasta_fn)


def crop_range() -> None:
    """Обрезает residues в selection и обновляет CIF/FASTA."""
    def delete_fn(chains: list[str]) -> None:
        cmd.remove("sele")

    def fasta_fn(records, chains):
        for chain in chains:
            if chain in records:
                new_seq = _get_sequence_from_pymol(chain)
                update_sequence(records, chain, new_seq)
        return records

    _run_cleanup_pipeline(delete_fn, fasta_fn)

