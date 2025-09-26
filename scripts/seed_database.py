import asyncio
import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import db_manager


async def seed_database():
    """Заполнение базы тестовыми данными"""

    try:
        with open('seed_test_data.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()

        queries = []
        current_query = []

        for line in sql_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            current_query.append(line)

            if line.endswith(';'):
                full_query = ' '.join(current_query)
                queries.append(full_query)
                current_query = []

        if current_query:
            full_query = ' '.join(current_query)
            queries.append(full_query)

        print(f"Найдено {len(queries)} запросов для выполнения")

        for i, query in enumerate(queries, 1):
            try:
                async with db_manager.engine.begin() as conn:
                    await conn.execute(text(query))
                    print(f"✅ Запрос {i}/{len(queries)} выполнен успешно")

            except Exception as e:
                print(f"❌ Ошибка в запросе {i}:")
                print(f"   Запрос: {query[:100]}...")
                print(f"   Ошибка: {e}")

        print("\n🎉 База данных успешно заполнена тестовыми данными!")

    except FileNotFoundError:
        print("❌ Файл seed_test_data.sql не найден")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(seed_database())