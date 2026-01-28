#!/usr/bin/env python3

import functools


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка: ключ не найден - {e}")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except FileNotFoundError as e:
            print(f"Ошибка: файл не найден - {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None

    return wrapper

