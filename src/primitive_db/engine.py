#!/usr/bin/env python3

import shlex

from prettytable import PrettyTable

from src.decorators import create_cacher
from src.primitive_db.constants import META_PATH
from src.primitive_db.core import (
    _ensure_schema,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from src.primitive_db.parser import (
    parse_multiple_conditions,
    parse_set_clause,
    parse_where_clause,
)
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

select_cacher = create_cacher()


def _print_help() -> None:
    """Выводит справку по доступным командам."""
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print("<command> tables - список таблиц")
    print(
        "<command> create <table> <col:type> [<col:type> ...] - "
        "создать таблицу (ID:int добавляется автоматически)"
    )
    print("<command> drop <table> - удалить таблицу")
    print("<command> describe <table> - показать структуру таблицы")
    print("<command> insert <table> <v1> <v2> ... - добавить запись")
    print("<command> select <table> [WHERE col = value] - вывести записи")
    print(
        "<command> update <table> SET col = value WHERE col = value - "
        "обновить записи"
    )
    print("<command> delete <table> WHERE col = value - удалить записи")


def _cmd_tables(meta: dict) -> None:
    """Обрабатывает команду tables: выводит список таблиц."""
    tables = sorted(meta["tables"].keys())
    if not tables:
        print("Таблиц пока нет.")
        return
    for name in tables:
        print(name)


def _cmd_describe(meta: dict, table_name: str) -> None:
    """Обрабатывает команду describe: выводит структуру таблицы."""
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
    """Приветствие и справка, затем запуск основного цикла."""
    print("Первая попытка запустить проект!")
    print("***")
    _print_help()
    run()


def run() -> None:
    """Основной цикл: чтение команд, разбор и вызов обработчиков."""
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
                    print(
                        f"Ошибка: неверный формат колонки '{spec}'. "
                        "Нужно name:type (без пробелов)"
                    )
                    ok = False
                    break
                name, typ = spec.split(":", 1)
                cols.append((name.strip(), typ.strip()))

            if not ok:
                continue

            existed_before = table_name in meta.get("tables", {})

            meta2 = create_table(meta, table_name, cols)

            created_now = (
                (not existed_before) and (table_name in meta2.get("tables", {}))
            )
            if created_now:
                save_metadata(META_PATH, meta2)
                print(f"Таблица '{table_name}' создана.")

            continue

        elif cmd == "drop":
            if len(args) != 1:
                print("Ошибка: используйте drop <table>")
                continue

            table_name = args[0]
            existed = "tables" in meta and table_name in meta.get("tables", {})

            new_meta = drop_table(meta, table_name)

            if new_meta is None:
                continue

            if (
                existed
                and "tables" in new_meta
                and table_name not in new_meta["tables"]
            ):
                save_metadata(META_PATH, new_meta)
                print(f"Таблица '{table_name}' удалена.")
            elif not existed:
                print(f"Таблица '{table_name}' не существовала.")

            continue

        elif cmd == "select":

            if len(args) < 1:
                print("Ошибка: используйте select <table> [WHERE column = value]")
                continue

            table_name = args[0]
            if table_name not in meta.get("tables", {}):
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            table_data = load_table_data(table_name)

            where_clause = None
            if len(args) > 1:
                where_str = " ".join(args[1:]).strip()
                if where_str.upper().startswith("WHERE"):
                    where_str = where_str[5:].strip()

                try:
                    where_clause = parse_multiple_conditions(
                        where_str, parse_where_clause
                    )
                except ValueError as e:
                    print(f"Ошибка парсинга WHERE: {e}")
                    continue

            if where_clause:
                cache_key = (table_name, frozenset(where_clause.items()))
            else:
                cache_key = (table_name, frozenset())
            result = select_cacher(
                cache_key,
                lambda: select(table_data, where_clause),
            )

            if not result:
                print("Записей не найдено.")
                continue

            if result:
                columns = list(result[0].keys())
                pt = PrettyTable(columns)
                for row in result:
                    pt.add_row([row.get(c) for c in columns])
                print(pt)

            continue

        elif cmd == "update":
            if len(args) < 2:
                print(
                    "Ошибка: используйте update <table> SET col = value "
                    "WHERE col = value"
                )
                continue

            table_name = args[0]
            if table_name not in meta.get("tables", {}):
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            cmd_str = " ".join(args[1:]).strip()
            cmd_up = cmd_str.upper()

            set_pos = cmd_up.find("SET")
            where_pos = cmd_up.find("WHERE")

            if set_pos == -1:
                print("Ошибка: требуется ключевое слово SET")
                continue

            if where_pos != -1:
                set_str = cmd_str[set_pos + 3 : where_pos].strip()
                where_str = cmd_str[where_pos + 5 :].strip()
            else:
                set_str = cmd_str[set_pos + 3 :].strip()
                where_str = ""

            try:
                set_clause = parse_set_clause(set_str)
                where_clause = (
                    parse_multiple_conditions(where_str, parse_where_clause)
                    if where_str
                    else {}
                )
            except Exception as e:
                print(f"Ошибка парсинга SET/WHERE: {e}")
                continue

            table_data = load_table_data(table_name)
            new_data = update(table_data, set_clause, where_clause)
            save_table_data(table_name, new_data)
            print("Записи обновлены.")
            continue

        elif cmd == "delete":
            if len(args) < 2:
                print("Ошибка: используйте delete <table> WHERE column = value")
                continue

            table_name = args[0]
            if table_name not in meta.get("tables", {}):
                print(f"Ошибка: таблица '{table_name}' не существует.")
                continue

            where_str = " ".join(args[1:]).strip()
            if where_str.upper().startswith("WHERE"):
                where_str = where_str[5:].strip()

            try:
                where_clause = parse_multiple_conditions(where_str, parse_where_clause)
            except ValueError as e:
                print(f"Ошибка парсинга WHERE: {e}")
                continue

            table_data = load_table_data(table_name)
            new_data = delete(table_data, where_clause)

            if new_data is None:
                continue

            if not isinstance(new_data, list):
                print("Ошибка: функция delete вернула неверный тип данных.")
                continue

            save_table_data(table_name, new_data)
            print("Записи удалены.")
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
                save_table_data(table_name, table_data)
                print("Запись добавлена.")

            except Exception as e:
                print(f"Ошибка вставки: {e}")

            continue

        else:
            print("Неизвестная команда. Введите help для списка команд.")
            continue
