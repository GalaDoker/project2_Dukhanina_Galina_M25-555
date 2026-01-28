#!/usr/bin/env python3

import json


def load_metadata(filepath):
    """
    Загружает данные из JSON-файла.
    
    Args:
        filepath (str): Путь к JSON-файлу
        
    Returns:
        dict: Загруженные данные или пустой словарь, если файл не найден
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """
    Сохраняет переданные данные в JSON-файл.
    
    Args:
        filepath (str): Путь к JSON-файлу
        data (dict): Данные для сохранения
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
