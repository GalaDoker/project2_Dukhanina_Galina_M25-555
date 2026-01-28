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
    """Запуск приложения, цикл команд и парсинг."""
    print("Первая попытка запустить проект!")
    print("***")
    _print_help()

    meta = _ensure_schema(load_metadata(META_PATH))

    while True:
        try:
            raw = input("Введите команду: ").strip()
        except EOFError:
            print()
            break

        if not raw:
            continue

        parts = shlex.split(raw)
        cmd = parts[0]

        if cmd == "exit":
            break

        if cmd == "help":
            _print_help()
            continue

        if cmd == "tables":
            _cmd_tables(meta)
            continue

        if cmd == "describe":
            if len(parts) != 2:
                print("Ошибка: используйте describe <table>")
                continue
            _cmd_describe(meta, parts[1])
            continue

        if cmd == "create":
            if len(parts) < 3:
                print("Ошибка: используйте create <table> <col:type> [<col:type> ...]")
                continue

            table_name = parts[1]
            specs = parts[2:]

            cols = []
            for spec in specs:
                if ":" not in spec:
                    print(f"Ошибка: неверный формат колонки '{spec}'. Нужно name:type")
                    cols = None
                    break
                n, t = spec.split(":", 1)
                cols.append((n.strip(), t.strip()))

            if cols is None:
                continue

            meta = create_table(meta, table_name, cols)
            save_metadata(META_PATH, meta)
            continue

        if cmd == "drop":
            if len(parts) != 2:
                print("Ошибка: используйте drop <table>")
                continue

            meta = drop_table(meta, parts[1])
            save_metadata(META_PATH, meta)
            continue

        print("Неизвестная команда. Введите help для списка команд.")
