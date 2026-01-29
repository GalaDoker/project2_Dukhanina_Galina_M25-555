#!/usr/bin/env python3

import functools
import time

def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result
    return wrapper

def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка: ключ не найден - {e}")
            if 'metadata' in str(func.__name__) or 'table' in str(func.__name__):
                return args[0] if args else {}
            return []
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            if 'metadata' in str(func.__name__) or 'table' in str(func.__name__):
                return args[0] if args else {}
            return []
        except FileNotFoundError as e:
            print(f"Ошибка: файл не найден - {e}")
            if 'metadata' in str(func.__name__) or 'table' in str(func.__name__):
                return args[0] if args else {}
            return []
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            if 'metadata' in str(func.__name__) or 'table' in str(func.__name__):
                return args[0] if args else {}
            return []

    return wrapper

def confirm_action(action_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                response = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ').strip().lower()
            except EOFError:
                print("Операция отменена (неинтерактивный режим).")
                return None

            if response != 'y':
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper
    return decorator
