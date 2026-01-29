#!/usr/bin/env python3

import re


def _parse_value(value_str: str):
    value_str = value_str.strip()

    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False
    
    try:
        return int(value_str)
    except ValueError:
        return value_str


def parse_where_clause(where_str: str) -> dict:
    if not where_str or not where_str.strip():
        return {}

    where_str = where_str.strip()

    parts = where_str.split("=", 1)
    if len(parts) != 2:
        raise ValueError(
            f"Неверный формат условия WHERE: '{where_str}'. "
            "Ожидается 'column = value'"
        )

    column = parts[0].strip()
    value_str = parts[1].strip()
    
    if not column:
        raise ValueError("Имя колонки не может быть пустым")
    
    value = _parse_value(value_str)
    
    return {column: value}


def parse_set_clause(set_str: str) -> dict:
    if not set_str or not set_str.strip():
        return {}

    set_str = set_str.strip()

    parts = set_str.split("=", 1)
    if len(parts) != 2:
        raise ValueError(
            f"Неверный формат условия SET: '{set_str}'. "
            "Ожидается 'column = value'"
        )

    column = parts[0].strip()
    value_str = parts[1].strip()
    
    if not column:
        raise ValueError("Имя колонки не может быть пустым")
    
    value = _parse_value(value_str)
    
    return {column: value}


def parse_multiple_conditions(conditions_str: str, parser_func) -> dict:
    if not conditions_str or not conditions_str.strip():
        return {}

    result = {}

    parts = re.split(r'\s+AND\s+', conditions_str, flags=re.IGNORECASE)
    
    for part in parts:
        part = part.strip()
        if part:
            parsed = parser_func(part)
            result.update(parsed)
    
    return result
