# Структура пакета PyMOL_tools

## Дерево файлов

```
PyMOL_tools/
├── __init__.py
├── core/
│   ├── browser.py
│   ├── cleanup.py
│   └── file_ops.py
├── commands/
│   ├── browser_cmds.py
│   ├── cleanup_cmds.py
│   └── file_ops_cmds.py
└── utils/
    ├── config.py
    ├── fasta_handler.py
    ├── pymol_utils.py
    └── welcome.py
```

## Структура модулей

| Модуль | Ключевые функции / классы | Назначение |
|---|---|---|
| `__init__.py` | `register_all_commands()` | Точка входа: регистрирует все команды при загрузке пакета и вызывает `show_welcome()`. |
| `core/browser.py` | `ProteinBrowser`<br>`browse()` | Ядро браузера: основная логика навигации по структурам. |
| `core/cleanup.py` | `_run_cleanup_pipeline()`<br>`cleanup_selected_chains()`<br>`remove_non_protein_components()`<br>`crop_range()` | Очистка структур: PyMOL-операции очистки и обрезки цепей, сохранение CIF/FASTA перед изменениями. |
| `core/file_ops.py` | `revert_to_original()`<br>`append_fasta_sequences()` | Файловые операции: откат к оригиналу, добавление FASTA-записей и работа с контекстом браузера. |
| `commands/browser_cmds.py` | `_browse_next()`<br>`_browse_prev()`<br>`_browse_first()`<br>`_browse_spec()`<br>`_browse_list()`<br>`_browse_color()`<br>`_show_fasta()`<br>`_show_browser_commands()` | Команды браузера: обёртки для регистрации команд навигации в PyMOL. |
| `commands/cleanup_cmds.py` | `_show_cleanup_commands()`<br>`_set_session_paths()`<br>`register_cleanup_commands()` | Команды очистки: обёртки для регистрации cleanup-команд в PyMOL. |
| `commands/file_ops_cmds.py` | `register_file_ops_commands()` | Команды файловых операций: обёртки для регистрации file_ops-команд в PyMOL. |
| `utils/config.py` | `Config`<br>`config` | Конфигурация: управление путями и настройками браузера. |
| `utils/fasta_handler.py` | `FastaRecord`<br>`extract_chain_ids()`<br>`edit_fasta_header()`<br>`parse_fasta()`<br>`serialize_fasta()`<br>`remove_chain()`<br>`update_sequence()`<br>`read_fasta_file()`<br>`write_fasta_file()` | Работа с FASTA: парсинг, сериализация и модификация FASTA-записей. Не зависит от PyMOL. |
| `utils/pymol_utils.py` | `get_browser()`<br>`set_browser()`<br>`get_current_object()`<br>`get_selected_chains()`<br>`save_cif()`<br>`_get_sequence_from_pymol()` | PyMOL-утилиты: вспомогательные функции для работы с контекстом PyMOL и глобальным браузером. |
| `utils/welcome.py` | `show_welcome()` | Приветствие: отображает справку о доступных командах при загрузке. |

## Удалённые файлы

| Файл | Причина |
|---|---|
| `core/fasta_edit.py` | `get_chains_from_current_obj()` перенесена в `pymol_utils.py`.<br>`filter_fasta_for_current_object()` заменена на `revert_to_original()` в `file_ops.py`. |
| `commands/fasta_cmds.py` | Заменён на `commands/file_ops_cmds.py`. |
| `PyMOL_tools.py` | Монолитный входной файл, заменён пакетом. |

## Границы слоёв

```
commands/          ← только cmd.extend, никакой логики
    ↓
core/              ← знает про браузер и/или cmd
    ↓
utils/             ← не знает про PyMOL-контекст (кроме pymol_utils)
```
