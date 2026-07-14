"""
Модуль для работы с FASTA-файлами.

Низкоуровневые функции (работа с контентом):
    - extract_chain_ids(header: str) -> list[str]
    - filter_fasta_by_chains(fasta_content: str, target_chains: list[str]) -> str
    - remove_chains_from_fasta(fasta_path: Path, chains_to_remove: list[str]) -> bool
    - append_fasta_content(fasta_path: Path, content: str) -> bool

Высокоуровневые функции (работа с сессией):
    - filter_original_fasta(obj_name: str, chains: list[str]) -> bool
"""
from pathlib import Path
import re


def extract_chain_ids(header: str) -> list[str]:
    """
    Извлекает auth chain IDs из заголовка FASTA.

    Примеры:
        >10FO_1|Chains A, C|... -> ['A', 'C']
        >10FO_2|Chain F[auth G]|... -> ['G']
        >10FO_3|Chains E[auth F], G[auth H]|... -> ['F', 'H']

    Args:
        header: Заголовок FASTA (строка, начинающаяся с >)

    Returns:
        Список auth chain IDs
    """
    # Паттерн для множественных цепей: "Chains A, C[auth X], E[auth Y]"
    multi_pattern = r'Chains?\s+([A-Z](?:\[[^\]]*\])?(?:\s*,\s*[A-Z](?:\[[^\]]*\])?)*)'

    # Паттерн для одиночной цепи: "Chain A[auth X]" или "Chain A"
    single_pattern = r'Chain\s+([A-Z](?:\[[^\]]*\])?)'

    auth_chains = []

    # Пробуем множественные цепи
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
        # Пробуем одиночную цепь
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

    Args:
        fasta_content: Содержимое FASTA файла
        target_chains: Список auth chain IDs для сохранения (например, ['A', 'B', 'F'])

    Returns:
        Отфильтрованный FASTA контент
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
        """Сохраняет текущую запись, если её цепи в target_set."""
        nonlocal current_header, current_sequence, current_auth_chains
        if current_header and set(current_auth_chains) & target_set:
            filtered_lines.append(current_header)
            filtered_lines.extend(current_sequence)
        current_header = None
        current_sequence = []
        current_auth_chains = []

    for line in lines:
        if line.startswith('>'):
            # Сохраняем предыдущую запись
            save_current()

            # Начинаем новую
            current_header = line
            current_auth_chains = extract_chain_ids(line)
        else:
            current_sequence.append(line)

    # Не забываем последнюю запись
    save_current()

    return '\n'.join(filtered_lines)


def remove_chains_from_fasta(fasta_path: Path, chains_to_remove: list[str]) -> bool:
    """
    Удаляет указанные цепи из FASTA-файла (редактирует заголовки).

    Если все цепи в заголовке удалены, удаляется и заголовок с последовательностью.

    Args:
        fasta_path: Путь к FASTA файлу
        chains_to_remove: Список цепей для удаления

    Returns:
        True если файл был изменён, False иначе
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
            skip_next_sequence = False
            new_line = _edit_fasta_header(line, chains_to_remove)
            if new_line != line:
                modified = True
            if new_line == "":
                modified = True
                skip_next_sequence = True
            else:
                new_lines.append(new_line)
        else:
            if skip_next_sequence:
                skip_next_sequence = False
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

    Поддерживаемые форматы:
        >10FO_2|Chains B, D|...           ->  >10FO_2|Chain D|... (если удаляем B)
        >10FO_2|Chain B|...               ->  >10FO_2|Chain B|... (если удаляем D)
        >9DVC_2|Chains B[auth C], F[auth O]|...  ->  >9DVC_2|Chain F[auth O]|... (если удаляем C)

    Если есть [auth X], проверяется X. Иначе проверяется базовый ID цепи.
    """
    # Паттерн для множественных цепей: "Chains B[auth C], F[auth O]" или "Chains B, D"
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
            return ""
        elif len(remaining) == 1:
            return f"Chain {remaining[0]}"
        else:
            return f"Chains {', '.join(remaining)}"

    new_header = re.sub(pattern_multi, replace_multi, header)

    # Паттерн для одиночной цепи
    pattern_single = r'(Chain)\s+([A-Z](?:\[[^\]]*\])?)'

    def replace_single(match):
        chain_entry = match.group(2)
        auth_match = re.search(r'\[auth\s*([A-Z])\]', chain_entry)
        if auth_match:
            chain_id = auth_match.group(1)
        else:
            chain_id = re.match(r'^([A-Z])', chain_entry).group(1)

        if chain_id in chains_to_remove:
            return ""
        return match.group(0)

    new_header = re.sub(pattern_single, replace_single, new_header)

    return new_header


def append_fasta_content(fasta_path: Path, content: str) -> bool:
    """
    Добавляет FASTA-записи в файл, проверяя на дубликаты по заголовку.

    Args:
        fasta_path: Путь к FASTA файлу
        content: FASTA контент для добавления

    Returns:
        True если записи были добавлены, False иначе
    """
    if not content:
        return False

    # Заменяем \\n на реальные переводы строки
    content = content.replace('\\n', '\n')

    # Парсим входные записи
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

    # Читаем существующие заголовки
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

    # Фильтруем дубликаты
    entries_to_add = []
    for entry in new_entries:
        header = entry.split('\n')[0]
        if header not in existing_headers:
            entries_to_add.append(entry)

    # Дописываем новые записи
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

    Логика:
    1. Читает оригинальный FASTA из fasta-sequences/
    2. Фильтрует по цепям из CIF объекта
    3. Добавляет отфильтрованный контент в fasta-filtered/

    Args:
        obj_name: Имя объекта (например, "8vul_cropped")
        chains: Список цепей из CIF файла

    Returns:
        True если успешно, False иначе
    """
    from config import config

    base_name = obj_name.replace("_cropped", "")
    original_fasta_path = config.get_fasta_original_folder() / f"{base_name}.fasta"
    target_fasta_path = config.get_fasta_folder() / f"{base_name}.fasta"

    # Читаем оригинальный FASTA
    try:
        with open(original_fasta_path, 'r') as f:
            original_content = f.read()
    except Exception as e:
        print(f"Ошибка чтения оригинального FASTA: {e}")
        return False

    # Фильтруем по цепям
    filtered_content = filter_fasta_by_chains(original_content, chains)

    if not filtered_content:
        print("Предупреждение: после фильтрации FASTA пуст")
        return False

    # Добавляем в целевой файл
    return append_fasta_content(target_fasta_path, filtered_content)
