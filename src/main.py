import os
import sys
import shlex
import argparse

VFS_NAME = "my-vfs"

def print_prompt():
    print(f"{VFS_NAME}> ", end="")

def cmd_ls(args):
    print(f"ls: {args}")
    return 0

def cmd_cd(args):
    print(f"cd: {args}")
    return 0

def cmd_exit(args):
    print("Выход из эмулятора.")
    sys.exit(0)

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

def parse_line(line):
    try:
        parts = shlex.split(line)
    except ValueError as e:
        print(f"Ошибка разбора: {e}")
        return None, []

    if not parts:
        return None, []

    return parts[0], parts[1:]

def execute_line(line):
    command, args = parse_line(line)
    if command is None:
        return True
    if command in COMMANDS:
        COMMANDS[command](args)
        return True
    else:
        print(f"{command}: команда не найдена")
        return False

def run_repl():
    print(f"Эмулятор оболочки ОС (VFS: {VFS_NAME})")
    print("Введите 'exit' для выхода.\n")
    while True:
        try:
            print_prompt()
            line = input()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        execute_line(line)

def run_script(script_path):
    if not os.path.isfile(script_path):
        print(f"Ошибка: стартовый скрипт не найден: {script_path}")
        sys.exit(1)

    print(f"--- Выполнение стартового скрипта: {script_path} ---\n")

    with open(script_path, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue
            print(f"{VFS_NAME}> {line}")
            ok = execute_line(line)
            if not ok:
                print(f"\nОшибка в строке {line_num}: '{line}'. Выполнение остановлено.")
                sys.exit(1)

    print("\n--- Стартовый скрипт выполнен успешно ---")

def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС с VFS.")
    parser.add_argument("--vfs", type=str, default=None, help="Путь к VFS")
    parser.add_argument("--script", type=str, default=None, help="Путь к стартовому скрипту")
    return parser.parse_args()

def main():
    args = parse_args()
    print("=== Параметры запуска эмулятора ===")
    print(f"VFS: {args.vfs if args.vfs else '(не задан)'}")
    print(f"Скрипт: {args.script if args.script else '(не задан)'}")
    print("===================================\n")

    if args.script:
        run_script(args.script)
    else:
        run_repl()

if __name__ == "__main__":
    main()