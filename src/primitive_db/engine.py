#!/usr/bin/env python3

def welcome():
    """Welcome function that starts the program and handles command loop."""
    print("Первая попытка запустить проект!")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    while True:
        command = input("Введите команду: ").strip()
        
        if command == "exit":
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            # Для других команд пока просто продолжаем цикл
            pass
