"""
Модуль приветствия при загрузке PyMOL_tools.

Единая точка для отображения информации о доступных командах.
"""


def show_welcome():
    """Показывает приветственное сообщение при загрузке модуля."""
    print("\n" + "="*60)
    print("PyMOL_tools загружен!")
    print("="*60)
    print()
    print("Доступные команды:")
    print()
    print("  --- Браузер структур ---")
    print("  browse(folder_path)      - запустить браузер")
    print("  browse_next()            - следующая структура")
    print("  browse_prev()            - предыдущая структура")
    print("  browse_first()           - первая структура")
    print("  browse_load(n)           - загрузить структуру по номеру")
    print("  browse_list()            - показать список всех структур")
    print("  browse_color()           - раскрасить цепи")
    print("  show_fasta()             - показать FASTA")
    print()
    print("  --- Cleanup pipeline ---")
    print("  cleanup_selected()       - удалить выбранные цепи")
    print("  remove_non_protein()     - удалить не-белковые компоненты")
    print("  append_fasta(content)    - добавить FASTA-записи")
    print()
    print("  --- Редактирование FASTA ---")
    print("  fasta_modify()           - отфильтровать FASTA по цепям")
    print()
    print("  --- Утилиты ---")
    print("  set_paths(...)           - установить кастомные пути")
    print()
    print("Для подробной информации вызовите:")
    print("  show_browser_commands()")
    print("  show_cleanup_commands()")
    print("  show_fasta_edit_commands()")
    print()
    print("="*60 + "\n")
