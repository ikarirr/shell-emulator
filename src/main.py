import os
import sys
import shlex
import json
import argparse
from datetime import datetime

# ==========================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (СОСТОЯНИЕ VFS)
# ==========================================
VFS_NAME = "my-vfs"
VFS_ROOT = None
CURRENT_PATH = "/"

# ==========================================
# БАЗОВЫЕ ФУНКЦИИ VFS (ВИРТУАЛЬНОЙ ФС)
# ==========================================
def make_default_vfs():
    """Создаёт структуру виртуальной файловой системы по умолчанию."""
    return {
        "type": "dir",
        "children": {
            "home": {
                "type": "dir",
                "children": {
                    "user": {
                        "type": "dir",
                        "children": {
                            "readme.txt": {
                                "type": "file",
                                "content": "Добро пожаловать в my-vfs!\n"
                            }
                        }
                    }
                }
            },
            "etc": {
                "type": "dir",
                "children": {
                    "config.json": {
                        "type": "file",
                        "content": '{"version": "1.0"}\n'
                    }
                }
            }
        }
    }

def load_vfs(filepath):
    """Загружает VFS из JSON-файла."""
    if not os.path.exists(filepath):
        print(f"Ошибка: файл {filepath} не найден.")
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_vfs(filepath):
    """Сохраняет текущее состояние VFS в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(VFS_ROOT, f, ensure_ascii=False, indent=4)

def get_node(path):
    """Возвращает узел (файл или папку) по указанному пути."""
    if path == "/":
        return VFS_ROOT
    parts = [p for p in path.split("/") if p]
    node = VFS_ROOT
    for part in parts:
        if node.get("type") != "dir" or part not in node.get("children", {}):
            return None
        node = node["children"][part]
    return node

def resolve_path(current, target):
    """Преобразует относительный путь в абсолютный."""
    if target.startswith("/"):
        return target
    if target == "..":
        return os.path.dirname(current) or "/"
    if target == ".":
        return current
    if current == "/":
        return "/" + target
    return current + "/" + target

# ==========================================
# КОМАНДЫ ЭМУЛЯТОРА
# ==========================================
def cmd_ls(args):
    """Показывает содержимое текущей папки."""
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
    """Меняет текущую директорию."""
    global CURRENT_PATH
    if not args:
        CURRENT_PATH = "/"
        return 0
    target = resolve_path(CURRENT_PATH, args[0])
    node = get_node(target)
    
    if node is None or node.get("type") != "dir":
        print(f"cd: {args[0]}: нет такого каталога")
        return 1
    CURRENT_PATH = target
    return 0

def cmd_pwd(args):
    """Показывает текущий путь."""
    print(CURRENT_PATH)
    return 0

def cmd_find(args):
    """Ищет файл или папку по имени."""
    if not args:
        print("find: не указано имя для поиска")
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
    """Показывает содержимое файла в обратном порядке."""
    if not args:
        print("tac: не указан файл")
        return 1
    path = resolve_path(CURRENT_PATH, args[0])
    node = get_node(path)
    
    if node is None or node.get("type") != "file":
        print(f"tac: {args[0]}: нет такого файла")
        return 1
    lines = node.get("content", "").splitlines()
    for line in reversed(lines):
        print(line)
    return 0

def cmd_date(args):
    """Показывает текущую дату и время."""
    now = datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
    return 0

def cmd_mv(args):
    """Перемещает/переименовывает файл или папку."""
    if len(args) < 2:
        print("mv: не указаны источник и назначение")
        return 1
    src_path = resolve_path(CURRENT_PATH, args[0])
    dst_path = resolve_path(CURRENT_PATH, args[1])
    
    src_node = get_node(src_path)
    if src_node is None:
        print(f"mv: {args[0]}: нет такого файла или каталога")
        return 1
        
    parent_path = os.path.dirname(src_path) or "/"
    if parent_path == "":
        parent_path = "/"
    parent_node = get_node(parent_path)
    
    if parent_node is None or parent_node.get("type") != "dir":
        print(f"mv: не удалось найти родительскую папку для {args[0]}")
        return 1
        
    name = os.path.basename(src_path)
    if name in parent_node.get("children", {}):
        del parent_node["children"][name]
        
    dst_parent_path = os.path.dirname(dst_path) or "/"
    if dst_parent_path == "":
        dst_parent_path = "/"
    dst_parent_node = get_node(dst_parent_path)
    
    if dst_parent_node is None or dst_parent_node.get("type") != "dir":
        print(f"mv: не удалось найти папку назначения для {args[1]}")
        return 1
        
    dst_name = os.path.basename(dst_path)
    if "children" not in dst_parent_node:
        dst_parent_node["children"] = {}
    dst_parent_node["children"][dst_name] = src_node
    print(f"Перемещено: {args[0]} -> {args[1]}")
    return 0

def cmd_exit(args):
    """Выход из эмулятора."""
    print("Выход из эмулятора.")
    sys.exit(0)

# Словарь доступных команд
COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "find": cmd_find,
    "tac": cmd_tac,
    "date": cmd_date,
    "mv": cmd_mv,
    "exit": cmd_exit,
}

# ==========================================
# ЯДРО ЭМУЛЯТОРА (PARSER & REPL)
# ==========================================
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

def execute_line(line):
    """Выполняет одну строку команды."""
    command, args = parse_line(line)
    if command is None:
        return True
    if command in COMMANDS:
        return COMMANDS[command](args) == 0
    print(f"{command}: команда не найдена")
    return True

def run_repl():
    """Цикл чтения-выполнения-печати (REPL)."""
    print(f"Эмулятор оболочки ОС (VFS: {VFS_NAME})")
    print("Введите 'exit' для выхода.\n")
    while True:
        try:
            line = input(f"{VFS_NAME}> ")
            if not execute_line(line):
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break

def run_script(filepath):
    """Выполняет команды из файла."""
    if not os.path.exists(filepath):
        print(f"Ошибка: файл сценария {filepath} не найден.")
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(f"{VFS_NAME}> {line}")
            execute_line(line)

# ==========================================
# ТОЧКА ВХОДА
# ==========================================
def main():
    global VFS_ROOT
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС с VFS.")
    parser.add_argument("--vfs", type=str, help="Путь к JSON-файлу виртуальной ФС.")
    parser.add_argument("--script", type=str, help="Путь к файлу со сценарием команд.")
    args = parser.parse_args()

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