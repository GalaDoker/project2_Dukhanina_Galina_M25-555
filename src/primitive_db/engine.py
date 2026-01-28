#!/usr/bin/env python3

import shlex

from src.primitive_db.utils import load_metadata, save_metadata, load_table_data, save_table_data
from src.primitive_db.core import _ensure_schema, create_table, drop_table, insert
from src.primitive_db.parser import parse_where_clause, parse_set_clause, parse_multiple_conditions

META_PATH = "db_meta.json"


def _print_help() -> None:
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print("<command> tables - список таблиц")
    print("<command> create <table> <col:type> [<col:type> ...] - создать таблицу (ID:int добавляется автоматически)")
    print("<command> drop <table> - удалить таблицу")
    print("<command> describe <table> - показать структуру таблицы")
    print("<command> insert <table> <v1> <v2> ... - добавить запись")

def _cmd_tables(meta: dict) -> None:
    tables = sorted(meta["tables"].keys())
    if not tables:
        print("Таблиц пока нет.")
        return
    for name in tables:
        print(name)


def _cmd_describe(meta: dict, table_name: str) -> None:
    if table_name not in meta["tables"]:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return

    cols = meta["tables"][table_name].get("columns", [])
    print(f"Таблица '{table_name}':")

    for c in cols:
        if isinstance(c, dict):
            name = c.get("name")
            typ = c.get("type")

        elif isinstance(c, (tuple, list)) and len(c) == 2:
            name, typ = c[0], c[1]

        elif isinstance(c, str) and ":" in c:
            name, typ = c.split(":", 1)
            name = name.strip()
            typ = typ.strip()

        else:
            print(f"- {c}")
            continue

        print(f"- {name}:{typ}")

def welcome() -> None:
    print("Первая попытка запустить проект!")
    print("***")
    _print_help()
    run()


def run() -> None:
    while True:
        meta = _ensure_schema(load_metadata(META_PATH))

        try:
            raw = input("Введите команду: ").strip()
        except EOFError:
            print()
            break

        if not raw:
            continue

        parts = shlex.split(raw)
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            break

        elif cmd == "help":
            _print_help()
            continue

        elif cmd == "tables":
            _cmd_tables(meta)
            continue

        elif cmd == "describe":
            if len(args) != 1:
                print("Ошибка: используйте describe <table>")
                continue
            _cmd_describe(meta, args[0])
            continue

        elif cmd == "create":
            if len(args) < 2:
                print("Ошибка: используйте create <table> <col:type> [<col:type> ...]")
                continue

            table_name = args[0]
            col_specs = args[1:]

            cols = []
            ok = True
            for spec in col_specs:
                if ":" not in spec:
                    print(f"Ошибка: неверный формат колонки '{spec}'. Нужно name:type (без пробелов)")
                    ok = False
                    break
                name, typ = spec.split(":", 1)
                cols.append((name.strip(), typ.strip()))

            if not ok:
                continue

            existed_before = table_name in meta.get("tables", {})

            meta2 = create_table(meta, table_name, cols)

            created_now = (not existed_before) and (table_name in meta2.get("tables", {}))
            if created_now:
                save_metadata(META_PATH, meta2)
                print(f"Таблица '{table_name}' создана.")

            continue

        elif cmd == "drop":
            if len(args) != 1:
                print("Ошибка: используйте drop <table>")
                continue

            table_name = args[0]
            existed = "tables" in meta and table_name in meta["tables"]

            old_meta = meta
            meta = drop_table(meta, table_name)

            if existed and "tables" in meta and table_name not in meta["tables"]:
                save_metadata(META_PATH, meta)
                print(f"Таблица '{table_name}' удалена.")
            else:
                meta = old_meta

            continue

        elif cmd == "select":

            if len(args) < 1:
                print("Ошибка: используйте select <table> [WHERE column = value]")
                continue

            table_name = args[0]

            if table_name not in meta["tables"]:
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            table_data = load_table_data(table_name)

            where_clause = None
            if len(args) > 1:
                where_str = " ".join(args[1:])

                if where_str.upper().startswith("WHERE"):
                    where_str = where_str[5:].strip()
                try:
                    where_clause = parse_multiple_conditions(where_str, parse_where_clause)
                except ValueError as e:
                    print(f"Ошибка парсинга WHERE: {e}")
                    continue

            result = select(table_data, where_clause)

            from prettytable import PrettyTable

            if result:
                cols = list(result[0].keys())
                pt = PrettyTable(cols)
                for row in result:
                    pt.add_row([row.get(col) for col in cols])
                print(pt)
            else:
                print("Записей не найдено.")

            continue

        elif cmd == "update":
            if len(args) < 5:
                print("Ошибка: используйте update <table> SET column = value WHERE column = value")
                continue

            table_name = args[0]

            if table_name not in meta["tables"]:
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            cmd_str = " ".join(args)
            set_idx = cmd_str.upper().find("SET")
            where_idx = cmd_str.upper().find("WHERE")

            if set_idx == -1:
                print("Ошибка: не найдено ключевое слово SET")
                continue

            set_str = cmd_str[set_idx + 3:where_idx].strip() if where_idx != -1 else cmd_str[set_idx + 3:].strip()
            where_str = cmd_str[where_idx + 5:].strip() if where_idx != -1 else ""

            try:
                set_clause = parse_set_clause(set_str)
                where_clause = parse_multiple_conditions(where_str, parse_where_clause) if where_str else {}
            except ValueError as e:
                print(f"Ошибка парсинга: {e}")
                continue

            table_data = load_table_data(table_name)
            table_data = update(table_data, set_clause, where_clause)
            save_table_data(table_name, table_data)
            print(f"Обновлено записей в таблице '{table_name}'.")
            continue

        elif cmd == "delete":
            if len(args) < 3:
                print("Ошибка: используйте delete <table> WHERE column = value")
                continue

            table_name = args[0]

            if table_name not in meta["tables"]:
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            where_str = " ".join(args[1:])
            if where_str.upper().startswith("WHERE"):
                where_str = where_str[5:].strip()

            try:
                where_clause = parse_multiple_conditions(where_str, parse_where_clause)
            except ValueError as e:
                print(f"Ошибка парсинга WHERE: {e}")
                continue

            table_data = load_table_data(table_name)
            table_data = delete(table_data, where_clause)
            save_table_data(table_name, table_data)
            print(f"Удалено записей из таблицы '{table_name}'.")
            continue

        elif cmd == "insert":
            if len(args) < 2:
                print("Ошибка: используйте insert <table> <v1> <v2> ...")
                continue

            table_name = args[0]
            values = args[1:]

            if table_name not in meta.get("tables", {}):
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            try:
                table_data = insert(meta, table_name, values)
                print("Запись добавлена.")
            except Exception as e:
                print(f"Ошибка вставки: {e}")

            continue

        else:
            print("Неизвестная команда. Введите help для списка команд.")
            continue
