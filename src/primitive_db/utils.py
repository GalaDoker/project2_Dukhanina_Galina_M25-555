#!/usr/bin/env python3

import os
import json

DATA_DIR = "data"

def load_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def load_table_data(table_name: str):
    
    _ensure_data_dir()
    filename = f"{table_name}.json"
    filepath = os.path.join(DATA_DIR, filename)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data) -> None:
    
    _ensure_data_dir()
    filename = f"{table_name}.json"
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
