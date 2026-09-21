import os
import sys
import shlex

VFS_NAME = "my-vfs"

def print_prompt():
    """Приглашение к вводу с именем VFS."""
    print(f"{VFS_NAME}> ", end="")

def cmd_ls(args):
    """Заглушка ls — выводит имя команды и аргументы."""
    print(f"ls: {args}")

def cmd_cd(args):
    """Заглушка cd — выводит имя команды и аргументы."""
    print(f"cd: {args}")

def cmd_exit(args):
    """Выход из эмулятора."""
    print("Выход из эмулятора.")
    sys.exit(0)

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

def parse_line(line):
    """Разбирает строку на команду и аргументы (с учётом кавычек)."""
    try:
        parts = shlex.split(line)
    except ValueError as e:
        print(f"Ошибка разбора: {e}")
        return None, []

    if not parts:
        return None, []

    return parts[0], parts[1:]

def run_repl():
    """Главный цикл REPL."""
    print(f"Эмулятор оболочки ОС (VFS: {VFS_NAME})")
    print("Введите 'exit' для выхода.\n")

    while True:
        try:
            print_prompt()
            line = input()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        command, args = parse_line(line)

        if command is None:
            continue

        if command in COMMANDS:
            COMMANDS[command](args)
        else:
            print(f"{command}: команда не найдена")

if __name__ == "__main__":
    run_repl()