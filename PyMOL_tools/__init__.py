from .commands.browser_cmds import register_browser_commands
from .commands.cleanup_cmds import register_cleanup_commands
from .commands.file_ops_cmds import register_file_ops_commands
from .utils.welcome import show_welcome


def register_all_commands():
    register_browser_commands()
    register_cleanup_commands()
    register_file_ops_commands()


register_all_commands()
show_welcome()
