#!/usr/bin/env python3

from src.decorators import handle_db_errors
from src.primitive_db.utils import load_metadata, save_metadata
from src.primitive_db.utils import load_table_data, save_table_data

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

@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    
    metadata = _ensure_schema(metadata)

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("Ошибка: имя таблицы должно быть непустой строкой.")

    table_name = table_name.strip()

    if table_name in metadata["tables"]:
        raise ValueError(f"Ошибка: таблица '{table_name}' уже существует.")

    if not isinstance(columns, list):
        raise ValueError("Ошибка: columns должен быть списком.")

    parsed_columns = []

    parsed_columns.append({"name": "ID", "type": "int"})

    for col in columns:
        if isinstance(col, (tuple, list)) and len(col) == 2:
            col_name, col_type = col[0], col[1]

        elif isinstance(col, dict) and "name" in col and "type" in col:
            col_name, col_type = col["name"], col["type"]

        else:
            raise ValueError(
                "Ошибка: неверный формат колонки. "
                "Ожидается ('name','type') или {'name':..., 'type':...}."
            )

        if not isinstance(col_name, str) or not col_name.strip():
            raise ValueError("Ошибка: имя колонки должно быть непустой строкой.")

        col_name = col_name.strip()

        if col_name.upper() == "ID":
            raise ValueError("Ошибка: столбец ID добавляется автоматически, не указывайте его вручную.")

        if not isinstance(col_type, str) or not col_type.strip():
            raise ValueError("Ошибка: тип колонки должен быть непустой строкой.")

        col_type = col_type.strip()

        if col_type not in ALLOWED_TYPES:
            raise ValueError("Ошибка: неверный тип данных. Разрешены только int, str, bool.")

        parsed_columns.append({"name": col_name, "type": col_type})

    metadata["tables"][table_name] = {"columns": parsed_columns}
    return metadata


def add_table(filepath: str, table_name: str, columns: list) -> dict:
    meta = _ensure_schema(load_metadata(filepath))
    meta = create_table(meta, table_name, columns)
    save_metadata(filepath, meta)
    return meta

@handle_db_errors
def drop_table(metadata: dict, table_name: str) -> dict:
    metadata = _ensure_schema(metadata)

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("Ошибка: имя таблицы должно быть непустой строкой.")

    table_name = table_name.strip()

    if table_name not in metadata["tables"]:
        raise ValueError(f"Ошибка: таблица '{table_name}' не существует.")

    del metadata["tables"][table_name]
    return metadata

def _to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "t", "yes", "y", "1"):
            return True
        if s in ("false", "f", "no", "n", "0"):
            return False
    raise ValueError(f"Нельзя привести к bool: {v!r}")

TYPE_CASTERS = {
    "int": int,
    "str": str,
    "bool": _to_bool,
}

@handle_db_errors
def _get_table_schema(metadata: dict, table_name: str):
    tables = metadata.get("tables", {})
    if table_name not in tables:
        raise ValueError(f"Таблица '{table_name}' не существует.")

    raw_cols = tables[table_name].get("columns", [])
    cols = []

    for c in raw_cols:
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
            continue

        cols.append({"name": name, "type": typ})

    return cols


def _row_matches_where(row: dict, where_clause: dict | None) -> bool:
    if not where_clause:
        return True
    for key, expected in where_clause.items():
        if key not in row:
            return False
        if row[key] != expected:
            return False
    return True

@handle_db_errors
def insert(metadata: dict, table_name: str, values: list):
    cols = _get_table_schema(metadata, table_name)

    if not cols or cols[0]["name"] != "ID":
        raise ValueError("Первая колонка должна быть ID:int")

    data_cols = cols[1:]

    if len(values) != len(data_cols):
        raise ValueError(
            f"Ожидалось {len(data_cols)} значений, получено {len(values)}."
        )

    table_data = load_table_data(table_name)

    if table_data:
        max_id = max(row.get("ID", 0) for row in table_data)
    else:
        max_id = 0
    new_id = max_id + 1

    row = {"ID": new_id}
    for (col_def, raw_value) in zip(data_cols, values):
        col_name = col_def["name"]
        col_type = col_def["type"]

        if col_type not in TYPE_CASTERS:
            raise ValueError(f"Неподдерживаемый тип '{col_type}' для колонки '{col_name}'.")

        caster = TYPE_CASTERS[col_type]
        try:
            value = caster(raw_value)
        except Exception as exc:
            raise ValueError(
                f"Неверное значение '{raw_value}' для колонки '{col_name}:{col_type}': {exc}"
            ) from exc

        row[col_name] = value

    table_data.append(row)
    save_table_data(table_name, table_data)
    return table_data

@handle_db_errors
def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    if not where_clause:
        return list(table_data)

    result = []
    for row in table_data:
        if _row_matches_where(row, where_clause):
            result.append(row)
    return result

@handle_db_errors
def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict]:
    if not set_clause:
        return table_data

    for row in table_data:
        if _row_matches_where(row, where_clause):
            for key, value in set_clause.items():
                row[key] = value

    return table_data

@handle_db_errors
def delete(table_data: list[dict], where_clause: dict) -> list[dict]:
    if not where_clause:
        return table_data

    new_data = [row for row in table_data if not _row_matches_where(row, where_clause)]
    return new_data

def describe_table(filepath: str, table_name: str) -> dict:
    meta = _ensure_schema(load_metadata(filepath))

    if table_name not in meta["tables"]:
        raise ValueError(f"Ошибка: таблица '{table_name}' не существует.")

    return meta["tables"][table_name]
