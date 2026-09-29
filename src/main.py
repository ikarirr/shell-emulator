import os
import sys
import shlex
import argparse
import json
import datetime

VFS_NAME = "my-vfs"
VFS_ROOT = None
CURRENT_PATH = "/"


def make_default_vfs():
    return {"type": "dir", "children": {}}


def load_vfs(path):
    if not os.path.isfile(path):
        print(f"Ошибка: файл VFS не найден: {path}")
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Ошибка: неверный JSON: {e}")
        sys.exit(1)
    if not isinstance(data, dict) or "type" not in data:
        print("Ошибка: неверная структура VFS")
        sys.exit(1)
    return data


def split_path(path):
    return [p for p in path.split("/") if p and p != "."]


def resolve_path(start_path, target):
    if target.startswith("/"):
        parts = split_path(target)
    else:
        parts = split_path(start_path)
        for p in split_path(target):
            if p == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(p)
    return "/" + "/".join(parts)


def get_node(path):
    parts = split_path(path)
    node = VFS_ROOT
    for p in parts:
        if node.get("type") != "dir":
            return None
        children = node.get("children", {})
        if p not in children:
            return None
        node = children[p]
    return node


def cmd_ls(args):
    path = CURRENT_PATH
    if args:
        path = resolve_path(CURRENT_PATH, args[0])
    node = get_node(path)
    if node is None:
        print(f"ls: {path}: нет такого файла или каталога")
        return 1
    if node.get("type") != "dir":
        print(os.path.basename(path))
        return 0
    children = node.get("children", {})
    for name in sorted(children.keys()):
        if children[name].get("type") == "dir":
            print(f"{name}/")
        else:
            print(name)
    return 0


def cmd_cd(args):
    global CURRENT_PATH
    if not args:
        CURRENT_PATH = "/"
        return 0
    target = args[0]
    new_path = resolve_path(CURRENT_PATH, target)
    node = get_node(new_path)
    if node is None:
        print(f"cd: {target}: нет такого файла или каталога")
        return 1
    if node.get("type") != "dir":
        print(f"cd: {target}: не директория")
        return 1
    CURRENT_PATH = new_path
    return 0


def cmd_pwd(args):
    print(CURRENT_PATH)
    return 0


def cmd_find(args):
    if not args:
        print("find: нужен аргумент (имя)")
        return 1
    name = args[0]
    results = []

    def walk(path, node):
        if node.get("type") == "dir":
            for child_name, child in node.get("children", {}).items():
                if path == "/":
                    child_path = "/" + child_name
                else:
                    child_path = path + "/" + child_name
                if child_name == name:
                    results.append(child_path)
                walk(child_path, child)

    walk("/", VFS_ROOT)
    if not results:
        print(f"find: '{name}' не найдено")
        return 1
    for r in results:
        print(r)
    return 0


def cmd_tac(args):
    if not args:
        print("tac: нужен путь к файлу")
        return 1
    path = resolve_path(CURRENT_PATH, args[0])
    node = get_node(path)
    if node is None:
        print(f"tac: {args[0]}: нет такого файла")
        return 1
    if node.get("type") != "file":
        print(f"tac: {args[0]}: не является файлом")
        return 1
    content = node.get("content", "")
    lines = content.split("\n")
    for line in reversed(lines):
        print(line)
    return 0


def cmd_date(args):
    now = datetime.datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
    return 0


def cmd_exit(args):
    print("Выход из эмулятора.")
    sys.exit(0)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "find": cmd_find,
    "tac": cmd_tac,
    "date": cmd_date,
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
        return COMMANDS[command](args) == 0
    print(f"{command}: команда не найдена")
    return False


def print_prompt():
    print(f"{VFS_NAME}:{CURRENT_PATH}$ ", end="")


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
        print(f"Ошибка: скрипт не найден: {script_path}")
        sys.exit(1)
    print(f"--- Выполнение: {script_path} ---\n")
    with open(script_path, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            print(f"{VFS_NAME}:{CURRENT_PATH}$ {line}")
            if not execute_line(line):
                print(f"\nОшибка в строке {line_num}. Остановка.")
                sys.exit(1)
    print("\n--- Скрипт выполнен успешно ---")


def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС с VFS.")
    parser.add_argument("--vfs", type=str, default=None)
    parser.add_argument("--script", type=str, default=None)
    return parser.parse_args()


def main():
    global VFS_ROOT
    args = parse_args()
    print("=== Параметры запуска эмулятора ===")
    print(f"VFS: {args.vfs if args.vfs else '(по умолчанию)'}")
    print(f"Скрипт: {args.script if args.script else '(не задан)'}")
    print("===================================\n")
    if args.vfs:
        VFS_ROOT = load_vfs(args.vfs)
    else:
        VFS_ROOT = make_default_vfs()
    if args.script:
        run_script(args.script)
    else:
        run_repl()


if __name__ == "__main__":
    main()