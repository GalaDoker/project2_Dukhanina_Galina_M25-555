## Управление таблицами

Приложение поддерживает команды для управления таблицами и их структурой.  
Метаданные таблиц хранятся в файле `db_meta.json`.

### Доступные команды

- **`help`** — вывод справочной информации
- **`exit`** — выход из программы
- **`tables`** — вывести список таблиц
- **`create <table> <col:type> [<col:type> ...]`** — создать таблицу  
  - столбец **`ID:int`** добавляется автоматически
  - разрешённые типы: **`int`**, **`str`**, **`bool`**
  - пример: `create users name:str age:int is_active:bool`
- **`describe <table>`** — показать структуру таблицы
- **`drop <table>`** — удалить таблицу

## CRUD-операции

Команды для работы с данными таблиц (записи хранятся в `data/<table>.json`).

- **`insert <table> <v1> <v2> ...`** — добавить запись
  Пример: `insert users "Alice" 25 true`

- **`select <table> [WHERE <условие>]`** — вывести записи (красивый вывод через prettytable)
  Примеры:
  - `select users`
  - `select users WHERE age = 25`
  - `select users WHERE name = "Alice"`

- **`update <table> SET <поле = значение> WHERE <условие>`** — обновить записи
  Пример: `update users SET age = 26 WHERE name = "Alice"`

- **`delete <table> WHERE <условие>`** — удалить записи
  Пример: `delete users WHERE name = "Bob"`

### Важно
- Строковые значения **всегда** указывайте в кавычках: `"Alice"`.
- Разрешённые типы столбцов: `int`, `str`, `bool`.

## Демонстрация установки пакета, запуска БД и управления таблицами:

https://asciinema.org/a/VJHVT7PnxENmTSHL 

## Демонстрация CRUD

https://asciinema.org/a/Wj1L8Qn3tyBiI3cx
