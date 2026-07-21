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
    print("  browse_spec(n)           - загрузить структуру по номеру")
    print("  browse_list()            - показать список всех структур")
    print("  browse_color()           - раскрасить цепи")
    print("  show_fasta()             - показать FASTA")
    print()
    print("  ---  Функции очистки ---")
    print("  cleanup_selected()       - удалить выбранные цепи")
    print("  crop_range()             - обрезать residues в sele")
    print("  remove_non_protein()     - удалить не-белковые компоненты")
    print()
    print(" --- Работа с файлами ---")
    print(" revert_to_original()        - откатить CIF и FASTA к оригиналу")
    print(" revert_to_original('cif')   - откатить только CIF")
    print(" revert_to_original('fasta') - откатить только FASTA")
    print(" append_fasta(content)       - добавить FASTA-записи в текущий объект")
    print()
    print("  --- Утилиты ---")
    print("  set_paths(...)           - установить кастомные пути")
    print()
    print("Для подробной информации вызовите:")
    print("  show_browser_commands()")
    print("  show_cleanup_commands()")
    print()
    print("="*60 + "\n")
