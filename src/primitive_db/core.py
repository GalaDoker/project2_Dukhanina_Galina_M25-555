#!/usr/bin/env python3
from src.primitive_db.utils import load_metadata, save_metadata


META_PATH = "db_meta.json"


def _ensure_schema(meta: dict) -> dict:
    """Гарантирует базовую структуру метаданных."""
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


def create_table(name: str, columns: list[str], filepath: str = META_PATH) -> None:
    if not name or not isinstance(name, str):
        raise ValueError("Имя таблицы должно быть непустой строкой.")
    if not columns or not isinstance(columns, list):
        raise ValueError("Колонки должны быть списком непустых строк.")
    if any((not isinstance(c, str) or not c.strip()) for c in columns):
        raise ValueError("Каждая колонка должна быть непустой строкой.")

    meta = _ensure_schema(load_metadata(filepath))
    if name in meta["tables"]:
        raise ValueError(f"Таблица '{name}' уже существует.")

    meta["tables"][name] = {"columns": [c.strip() for c in columns]}
    save_metadata(filepath, meta)


def drop_table(name: str, filepath: str = META_PATH) -> None:
    meta = _ensure_schema(load_metadata(filepath))
    if name not in meta["tables"]:
        raise ValueError(f"Таблица '{name}' не существует.")

    del meta["tables"][name]
    save_metadata(filepath, meta)


def describe_table(name: str, filepath: str = META_PATH) -> dict:
    meta = _ensure_schema(load_metadata(filepath))
    if name not in meta["tables"]:
        raise ValueError(f"Таблица '{name}' не существует.")
    return meta["tables"][name]
