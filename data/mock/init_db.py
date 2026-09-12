import os
import sqlite3
from pathlib import Path

def create_database(schema_file="schema.sql", db_file="bot_data.db"):
    """
    Создает пустую базу данных SQLite на основе SQL-скрипта.
    
    Args:
        schema_file (str): Имя файла со схемой (CREATE TABLE и т.д.)
        db_file (str): Имя создаваемого файла базы данных
    """
    # 1. Определяем пути относительно текущей директории скрипта
    base_dir = Path(__file__).resolve().parent
    schema_path = base_dir / schema_file
    db_path = base_dir / db_file

    # 2. Проверка существования файла схемы
    if not schema_path.exists():
        print(f"❌ Ошибка: Файл схемы '{schema_file}' не найден в директории {base_dir}")
        print("Убедитесь, что schema.sql лежит в корне проекта.")
        return False

    try:
        print(f"🗄️  Подключение к базе данных: {db_path}")
        
        # Если база уже существует, мы её перезапишем (удалим старую, создадим новую пустую)
        # Это важно для демо-проектов на GitHub, чтобы гарантировать чистую схему.
        if db_path.exists():
            print("⚠️  Обнаружена старая база данных. Она будет удалена и создана заново.")
            db_path.unlink()

        # 3. Подключение к SQLite (файл создастся автоматически)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 4. Чтение и выполнение SQL-скрипта
        # executescript() позволяет выполнить сразу несколько команд (CREATE TABLE, индексы и т.д.)
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        print("🚀 Выполнение SQL-скрипта...")
        cursor.executescript(sql_script)
        
        # 5. Фиксация изменений и закрытие соединения
        conn.commit()
        conn.close()

        print(f"✅ Успешно! База данных '{db_file}' создана.")
        print(f"📂  Расположение: {db_path.absolute()}")
        
        # Опционально: проверка созданных таблиц
        conn_check = sqlite3.connect(db_path)
        tables = conn_check.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        conn_check.close()
        print(f"📋 В базе создано таблиц: {len(tables)}")
        print("Таблицы:", [t for t in tables])

        return True

    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    create_database()
