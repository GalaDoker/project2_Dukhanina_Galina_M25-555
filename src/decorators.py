#!/usr/bin/env python3

import time


def _copy_func_attrs(wrapper, func):
    """Копирует __name__ и __doc__ с оборачиваемой функции на обёртку."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = getattr(func, "__doc__", None)


def log_time(func):
    """Декоратор: выводит время выполнения функции."""
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result

    _copy_func_attrs(wrapper, func)
    return wrapper


def handle_db_errors(func):
    """Декоратор: перехватывает исключения БД и выводит сообщения об ошибках."""
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

    _copy_func_attrs(wrapper, func)
    return wrapper


def confirm_action(action_name: str):
    """Декоратор: запрашивает подтверждение (y/n) перед выполнением функции."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                prompt = 'Вы уверены, что хотите выполнить "{}"? [y/n]: '
                msg = prompt.format(action_name)
                response = input(msg).strip().lower()
            except EOFError:
                print("Операция отменена (неинтерактивный режим).")
                return None

            if response != 'y':
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        _copy_func_attrs(wrapper, func)
        return wrapper
    return decorator


def create_cacher():
    """Замыкание для кэширования результатов (например, select)."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает значение по ключу из кэша или вычисляет и кэширует."""
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result
