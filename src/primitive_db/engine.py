#!/usr/bin/env python3

import shlex

from src.primitive_db.utils import load_metadata, save_metadata
from src.primitive_db.core import _ensure_schema, create_table, drop_table

META_PATH = "db_meta.json"


def _print_help() -> None:
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print("<command> tables - список таблиц")
    print("<command> create <table> <col:type> [<col:type> ...] - создать таблицу (ID:int добавляется автоматически)")
    print("<command> drop <table> - удалить таблицу")
    print("<command> describe <table> - показать структуру таблицы")


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
        print(f"- {c.get('name')}:{c.get('type')}")


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

            ols = []
            ok = True
            for spec in col_specs:
                if ":" not in spec:
                    print(f"Ошибка: неверный формат колонки '{spec}'. Нужно name:type")
                    ok = False
                    break
                name, typ = spec.split(":", 1)
                cols.append((name.strip(), typ.strip()))

            if not ok:
                continue

            old_meta = meta
            meta = create_table(meta, table_name, cols)

            if "tables" in meta and table_name in meta["tables"]:
                save_metadata(META_PATH, meta)
                print(f"Таблица '{table_name}' создана.")
            else:
                meta = old_meta

            continue

        elif cmd == "drop":
            if len(args) != 1:
                print("Ошибка: используйте drop <table>")
                continue

            table_name = args[0]
            existed = "tables" in meta and table_name in meta["tables"]

            meta = drop_table(meta, table_name)

            if existed and ("tables" in meta and table_name not in meta["tables"]):
                save_metadata(META_PATH, meta)
                print(f"Таблица '{table_name}' удалена.")

            continue

        else:
            print("Неизвестная команда. Введите help для списка команд.")
            continue
