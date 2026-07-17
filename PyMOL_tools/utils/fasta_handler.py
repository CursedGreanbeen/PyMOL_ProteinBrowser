"""
Модуль для работы с FASTA-файлами.

ТОЛЬКО низкоуровневые функции — без PyMOL cmd и регистрации.
"""
from pathlib import Path
import re


def extract_chain_ids(header: str) -> list[str]:
    """
    Извлекает auth chain IDs из заголовка FASTA.
    """
    multi_pattern = r'Chains?\s+([A-Z](?:\[[^\]]*\])?(?:\s*,\s*[A-Z](?:\[[^\]]*\])?)*)'
    single_pattern = r'Chain\s+([A-Z](?:\[[^\]]*\])?)'

    auth_chains = []

    multi_match = re.search(multi_pattern, header)
    if multi_match:
        chain_str = multi_match.group(1)
        entries = [c.strip() for c in chain_str.split(',')]
        for entry in entries:
            auth_match = re.search(r'\[auth\s*([A-Z])\]', entry)
            if auth_match:
                auth_chains.append(auth_match.group(1))
            else:
                match = re.match(r'^([A-Z])', entry)
                if match:
                    auth_chains.append(match.group(1))
    else:
        single_match = re.search(single_pattern, header)
        if single_match:
            entry = single_match.group(1)
            auth_match = re.search(r'\[auth\s*([A-Z])\]', entry)
            if auth_match:
                auth_chains.append(auth_match.group(1))
            else:
                match = re.match(r'^([A-Z])', entry)
                if match:
                    auth_chains.append(match.group(1))

    return auth_chains


def filter_fasta_by_chains(fasta_content: str, target_chains: list[str]) -> str:
    """
    Фильтрует FASTA контент, оставляя только записи с указанными auth chain IDs.
    """
    if not fasta_content:
        return ""

    target_set = set(c.upper() for c in target_chains)
    lines = fasta_content.split('\n')

    filtered_lines = []
    current_header = None
    current_sequence = []
    current_auth_chains = []

    def save_current():
        nonlocal current_header, current_sequence, current_auth_chains
        if current_header and set(current_auth_chains) & target_set:
            filtered_lines.append(current_header)
            filtered_lines.extend(current_sequence)
        current_header = None
        current_sequence = []
        current_auth_chains = []

    for line in lines:
        if line.startswith('>'):
            save_current()
            current_header = line
            current_auth_chains = extract_chain_ids(line)
        else:
            current_sequence.append(line)

    save_current()
    return '\n'.join(filtered_lines)


def remove_chains_from_fasta(fasta_path: Path, chains_to_remove: list[str]) -> bool:
    """
    Удаляет указанные цепи из FASTA-файла (редактирует заголовки).
    """
    try:
        with open(fasta_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка чтения FASTA: {e}")
        return False

    lines = content.split('\n')
    modified = False
    new_lines = []
    skip_next_sequence = False

    for line in lines:
        if line.startswith('>'):
            new_line = _edit_fasta_header(line, chains_to_remove)
            if new_line != line:
                modified = True
            if new_line == "":
                # Запись должна быть полностью удалена — пропускаем заголовок и последовательность
                modified = True
                skip_next_sequence = True
            else:
                new_lines.append(new_line)
                skip_next_sequence = False
        else:
            if skip_next_sequence:
                # Пропускаем строку последовательности
                continue
            else:
                new_lines.append(line)

    if modified:
        try:
            with open(fasta_path, 'w') as f:
                f.write('\n'.join(new_lines))
        except Exception as e:
            print(f"Ошибка сохранения FASTA: {e}")
            return False

    return modified


def _edit_fasta_header(header: str, chains_to_remove: set[str]) -> str:
    """
    Редактирует один заголовок FASTA, удаляя указанные цепи.

    Если все цепи удаляются — возвращает пустую строку (запись будет удалена).
    Если часть цепей остаётся — возвращает отредактированный заголовок.
    """
    pattern_multi = r'(Chains)\s+([A-Z](?:\[[^\]]*\])?(?:,\s*[A-Z](?:\[[^\]]*\])?)*)'

    def replace_multi(match):
        chains_str = match.group(2)
        chain_entries = [c.strip() for c in chains_str.split(',')]

        def get_check_id(entry):
            auth_match = re.search(r'\[auth\s*([A-Z])\]', entry)
            if auth_match:
                return auth_match.group(1)
            match = re.match(r'^([A-Z])', entry)
            return match.group(1) if match else entry

        remaining = [e for e in chain_entries if get_check_id(e) not in chains_to_remove]

        if not remaining:
            return "__DELETE_RECORD__"
        elif len(remaining) == 1:
            return f"Chain {remaining[0]}"
        else:
            return f"Chains {', '.join(remaining)}"

    new_header = re.sub(pattern_multi, replace_multi, header)

    # Если в multi-паттерне всё удалилось — возвращаем маркер
    if "__DELETE_RECORD__" in new_header:
        return ""

    pattern_single = r'(Chain)\s+([A-Z](?:\[[^\]]*\])?)'

    def replace_single(match):
        chain_entry = match.group(2)
        auth_match = re.search(r'\[auth\s*([A-Z])\]', chain_entry)
        if auth_match:
            chain_id = auth_match.group(1)
        else:
            chain_id = re.match(r'^([A-Z])', chain_entry).group(1)

        if chain_id in chains_to_remove:
            return "__DELETE_RECORD__"
        return match.group(0)

    new_header = re.sub(pattern_single, replace_single, new_header)

    # Если единственная цепь была удалена — возвращаем пустую строку
    if "__DELETE_RECORD__" in new_header:
        return ""

    return new_header


def append_fasta_content(fasta_path: Path, content: str) -> bool:
    """
    Добавляет FASTA-записи в файл, проверяя на дубликаты по заголовку.
    """
    if not content:
        return False

    content = content.replace('\\n', '\n')

    lines = content.split('\n')
    new_entries = []
    current_entry = []

    for line in lines:
        if line.startswith('>'):
            if current_entry:
                new_entries.append('\n'.join(current_entry))
            current_entry = [line]
        else:
            current_entry.append(line)

    if current_entry:
        new_entries.append('\n'.join(current_entry))

    try:
        with open(fasta_path, 'r') as f:
            existing_content = f.read()
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return False

    existing_headers = set()
    for line in existing_content.split('\n'):
        if line.startswith('>'):
            existing_headers.add(line)

    entries_to_add = []
    for entry in new_entries:
        header = entry.split('\n')[0]
        if header not in existing_headers:
            entries_to_add.append(entry)

    if entries_to_add:
        try:
            with open(fasta_path, 'a') as f:
                for entry in entries_to_add:
                    f.write(entry + '\n')
            return True
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")
            return False

    return False


def filter_original_fasta(obj_name: str, chains: list[str]) -> bool:
    """
    Фильтрует оригинальный FASTA под цепи объекта и добавляет в fasta-filtered/.
    """
    from .config import config

    base_name = obj_name.replace("_cropped", "")
    original_fasta_path = config.get_fasta_original_folder() / f"{base_name}.fasta"
    target_fasta_path = config.get_fasta_folder() / f"{base_name}.fasta"

    try:
        with open(original_fasta_path, 'r') as f:
            original_content = f.read()
    except Exception as e:
        print(f"Ошибка чтения оригинального FASTA: {e}")
        return False

    filtered_content = filter_fasta_by_chains(original_content, chains)

    if not filtered_content:
        print("Предупреждение: после фильтрации FASTA пуст")
        return False

    return append_fasta_content(target_fasta_path, filtered_content)


def update_fasta_sequences(fasta_path: Path, chain_sequences: dict[str, str]) -> bool:
    """
    Обновляет последовательности для указанных цепей в FASTA-файле.

    Заголовки остаются без изменений — обновляется только последовательность
    под заголовком, где в заголовке упоминается данная цепь.

    Args:
        fasta_path: Путь к FASTA-файлу
        chain_sequences: Словарь {chain_id: sequence}, например {'A': 'MKT...', 'B': 'GLS...'}

    Returns:
        bool: True если были обновления, False иначе
    """
    if not chain_sequences:
        return False

    try:
        with open(fasta_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка чтения FASTA: {e}")
        return False

    target_chains = set(chain_sequences.keys())
    lines = content.split('\n')
    new_lines = []
    modified = False

    current_auth_chains = []
    in_target_record = False

    for line in lines:
        if line.startswith('>'):
            current_auth_chains = extract_chain_ids(line)
            in_target_record = bool(set(current_auth_chains) & target_chains)
            new_lines.append(line)
        else:
            if in_target_record and current_auth_chains:
                # Ищем matching chain среди ВСЕХ auth_chains в заголовке
                matched = False
                for auth_chain in current_auth_chains:
                    if auth_chain in chain_sequences:
                        new_lines.append(chain_sequences[auth_chain])
                        modified = True
                        matched = True
                        break
                if not matched:
                    new_lines.append(line)
                in_target_record = False
            else:
                new_lines.append(line)

    if modified:
        try:
            with open(fasta_path, 'w') as f:
                f.write('\n'.join(new_lines))
            return True
        except Exception as e:
            print(f"Ошибка сохранения FASTA: {e}")
            return False

    return False
