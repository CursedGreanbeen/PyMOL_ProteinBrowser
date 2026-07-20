from pymol import cmd
from ..core.browser import ProteinBrowser

_browser_instance: ProteinBrowser | None = None


def get_browser() -> ProteinBrowser:
    """Возвращает глобальный экземпляр ProteinBrowser. Бросает RuntimeError если не инициализирован."""
    if _browser_instance is None:
        raise RuntimeError("Браузер не инициализирован. Сначала вызови browse(folder_path).")
    return _browser_instance


def set_browser(browser: ProteinBrowser) -> None:
    """Устанавливает глобальный экземпляр браузера. Вызывается из browse()."""
    global _browser_instance
    _browser_instance = browser


def get_current_object() -> str:
    """Возвращает имя текущего загруженного объекта из браузера."""
    return get_browser().current_obj_name


def get_selected_chains() -> list[str]:
    """Возвращает уникальные chain ids из текущего selection в PyMOL."""
    chains = []
    cmd.iterate("sele", "chains.append(chain)", space={"chains": chains})
    return list(set(chains))


def _get_sequence_from_pymol(obj_name: str, chain: str) -> str:
    """Забирает текущую последовательность цепи из PyMOL после обрезки."""
    fasta_str = cmd.get_fastastr(f"{obj_name} and chain {chain}")
    lines = fasta_str.strip().split('\n')
    return ''.join(lines[1:])


def save_cif(obj_name: str, path: str) -> None:
    """Сохраняет объект PyMOL в CIF-файл по указанному пути."""
    cmd.save(path, obj_name)
    print(f"[pymol_utils] Сохранено: {path}")
