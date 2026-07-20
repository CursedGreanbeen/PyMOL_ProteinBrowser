import shutil
from ..utils.pymol_utils import get_current_object
from ..utils.config import config


def revert_to_original(file_type: str = "both") -> None:
    """
    Откатывает файл(ы) текущего объекта к оригиналу.
    file_type: "cif", "fasta" или "both"
    """
    obj_name = get_current_object()

    if file_type in ("cif", "both"):
        src = config.get_original_cif_path(obj_name)
        dst = config.get_cif_path(obj_name)
        if src.exists():
            shutil.copy2(src, dst)
            print(f"[file_ops] CIF восстановлен: {dst}")
        else:
            print(f"[file_ops] Оригинал CIF не найден: {src}")

    if file_type in ("fasta", "both"):
        src = config.get_original_fasta_path(obj_name)
        dst = config.get_fasta_path(obj_name)
        if src.exists():
            shutil.copy2(src, dst)
            print(f"[file_ops] FASTA восстановлен: {dst}")
        else:
            print(f"[file_ops] Оригинал FASTA не найден: {src}")


def append_fasta_sequences(content: str) -> None:
    """Добавляет FASTA-записи в файл текущего объекта."""
    obj_name = get_current_object()
    fasta_path = config.get_fasta_path(obj_name)

    if not fasta_path.exists():
        print(f"[file_ops] FASTA-файл не найден: {fasta_path}")
        return

    with open(fasta_path, "a") as f:
        f.write("\n" + content.strip())
    print(f"[file_ops] FASTA дополнен: {fasta_path}")