#!/usr/bin/env python3


def _split_by_and(s: str) -> list:
    """Разбивает строку по ' AND ' (без учёта регистра); пробелы схлопываются в один."""
    s = " ".join(s.split())
    parts = []
    s_lower = s.lower()
    sep = " and "
    start = 0
    while True:
        idx = s_lower.find(sep, start)
        if idx == -1:
            part = s[start:].strip()
            if part:
                parts.append(part)
            break
        part = s[start:idx].strip()
        if part:
            parts.append(part)
        start = idx + len(sep)
    return parts


def _parse_value(value_str: str):
    """Преобразует строку в значение: число, bool или строка (в кавычках)."""
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
    """Разбирает условие WHERE вида 'column = value' в словарь {column: value}."""
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
    """Разбирает условие SET вида 'column = value' в словарь {column: value}."""
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
    """Разбирает несколько условий через AND и объединяет в один словарь."""
    if not conditions_str or not conditions_str.strip():
        return {}

    result = {}

    parts = _split_by_and(conditions_str)

    for part in parts:
        part = part.strip()
        if part:
            parsed = parser_func(part)
            result.update(parsed)

    return result
