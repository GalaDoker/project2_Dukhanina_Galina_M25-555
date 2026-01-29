#!/usr/bin/env python3

import json
import os

from src.primitive_db.constants import DATA_DIR, TABLE_FILE_EXT


def load_metadata(filepath):
    """Загружает метаданные БД из JSON; при отсутствии файла возвращает пустой dict."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные БД в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _ensure_data_dir() -> None:
    """Создаёт каталог для данных таблиц, если его нет."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_table_data(table_name: str):
    """Загружает данные таблицы из JSON; при отсутствии файла — пустой список."""
    _ensure_data_dir()
    filename = f"{table_name}{TABLE_FILE_EXT}"
    filepath = os.path.join(DATA_DIR, filename)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data) -> None:
    """Сохраняет данные таблицы в JSON-файл."""
    _ensure_data_dir()
    filename = f"{table_name}{TABLE_FILE_EXT}"
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
