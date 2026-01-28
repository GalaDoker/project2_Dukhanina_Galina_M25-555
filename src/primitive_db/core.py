#!/usr/bin/env python3

from src.primitive_db.utils import load_metadata, save_metadata

META_PATH = "db_meta.json"
ALLOWED_TYPES = {"int", "str", "bool"}


def _ensure_schema(meta: dict) -> dict:
    if not isinstance(meta, dict):
        meta = {}
    if "tables" not in meta or not isinstance(meta["tables"], dict):
        meta["tables"] = {}
    return meta


def list_tables(filepath: str = META_PATH) -> list[str]:
    meta = _ensure_schema(load_metadata(filepath))
    return sorted(meta["tables"].keys())


def table_exists(name: str, filepath: str = META_PATH) -> bool:
    meta = _ensure_schema(load_metadata(filepath))
    return name in meta["tables"]


def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    
    metadata = _ensure_schema(metadata)

    if not isinstance(table_name, str) or not table_name.strip():
        print("Ошибка: имя таблицы должно быть непустой строкой.")
        return metadata

    table_name = table_name.strip()

    if table_name in metadata["tables"]:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    if not isinstance(columns, list):
        print("Ошибка: columns должен быть списком.")
        return metadata

    parsed_columns = []

    parsed_columns.append({"name": "ID", "type": "int"})

    for col in columns:
        if isinstance(col, (tuple, list)) and len(col) == 2:
            col_name, col_type = col[0], col[1]

        elif isinstance(col, dict) and "name" in col and "type" in col:
            col_name, col_type = col["name"], col["type"]

        else:
            print(
                "Ошибка: неверный формат колонки. "
                "Ожидается ('name','type') или {'name':..., 'type':...}."
            )
            return metadata

        if not isinstance(col_name, str) or not col_name.strip():
            print("Ошибка: имя колонки должно быть непустой строкой.")
            return metadata

        col_name = col_name.strip()

        if col_name.upper() == "ID":
            print("Ошибка: столбец ID добавляется автоматически, не указывайте его вручную.")
            return metadata

        if not isinstance(col_type, str) or not col_type.strip():
            print("Ошибка: тип колонки должен быть непустой строкой.")
            return metadata

        col_type = col_type.strip()

        if col_type not in ALLOWED_TYPES:
            print("Ошибка: неверный тип данных. Разрешены только int, str, bool.")
            return metadata

        parsed_columns.append({"name": col_name, "type": col_type})

    metadata["tables"][table_name] = {"columns": parsed_columns}
    return metadata


def add_table(filepath: str, table_name: str, columns: list) -> dict:
    meta = _ensure_schema(load_metadata(filepath))
    meta = create_table(meta, table_name, columns)
    save_metadata(filepath, meta)
    return meta


def drop_table(metadata: dict, table_name: str) -> dict:
    metadata = _ensure_schema(metadata)

    if not isinstance(table_name, str) or not table_name.strip():
        print("Ошибка: имя таблицы должно быть непустой строкой.")
        return metadata

    table_name = table_name.strip()

    if table_name not in metadata["tables"]:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return metadata

    del metadata["tables"][table_name]
    return metadata


def describe_table(filepath: str, table_name: str) -> dict:
    meta = _ensure_schema(load_metadata(filepath))

    if table_name not in meta["tables"]:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return {}

    return meta["tables"][table_name]
