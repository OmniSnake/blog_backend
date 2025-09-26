# FastAPI Blog Backend

Бэкенд-приложение для блога с админскими CRUD-операциями, публичным API и системой управления пользователями.

## 🚀 Особенности

- **Полная CRUD система** для постов и категорий
- **JWT аутентификация** с access/refresh токенами
- **Ролевая система** (User, Admin)
- **Санитизация HTML** для защиты от XSS
- **Публичное API** для чтения постов
- **Админская панель** для управления контентом
- **Асинхронная архитектура** на FastAPI + SQLAlchemy 2.0
- **Полное покрытие тестами** (pytest)
- **Docker контейнеризация**
- **Миграции базы данных** (Alembic)

## 🛠 Технологический стек

- **Python 3.11+**
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy 2.0** - асинхронный ORM
- **PostgreSQL** - основная база данных
- **Alembic** - система миграций
- **JWT** - аутентификация
- **Pydantic v2** - валидация данных
- **Docker & Docker Compose** - контейнеризация
- **pytest** - тестирование

## 📁 Структура проекта
- blog-backend/
- app/ # Основное приложение
- app/api/ # API endpoints
- app/api/v1/ # Версия API v1
- app/core/ # Конфигурация и база данных
- app/models/ # SQLAlchemy модели
- app/repositories/ # Паттерн Repository (работа с данными)
- app/schemas/ # Pydantic схемы
- app/services/ # Бизнес-логика
- alembic/ # Миграции базы данных
- tests/ # Тесты
- scripts/ # Вспомогательные скрипты
- docker-compose.yml # Docker конфигурация


## 🚀 Быстрый старт

### Вариант 1: Запуск с Docker (рекомендуется)

```bash
# Клонирование репозитория
git clone https://github.com/OmniSnake/blog_backend
cd blog-backend

# Запуск всех сервисов
docker-compose up -d

# Применение миграций
docker-compose exec web alembic upgrade head

# Заполнение тестовыми данными
docker-compose exec web python scripts/seed_database.py

Приложение будет доступно по адресу: http://localhost:8000
```

### Вариант 2: Локальная установка
```bash
# Клонирование репозитория
git clone https://github.com/OmniSnake/blog_backend
cd blog-backend

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл при необходимости

# Запуск PostgreSQL (требуется установленный Docker)
docker-compose up -d db

# Применение миграций
alembic upgrade head

# Заполнение тестовыми данными
python scripts/seed_database.py

# Запуск приложения
python run.py
```

📚 API Документация
После запуска приложения доступны:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Health Check: http://localhost:8000/health

🔐 Аутентификация
Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "securepassword123",
       "first_name": "John",
       "last_name": "Doe"
     }'
```
Вход в систему
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "securepassword123"
     }'
```
Ответ содержит access и refresh токены:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

📡 API Endpoints

Публичные endpoints (не требуют аутентификации)

Метод	Endpoint	                    Описание
GET	    /api/v1/posts/	                Список опубликованных постов
GET	    /api/v1/posts/{slug}	        Получить пост по slug
GET	    /api/v1/categories/	            Список категорий
GET	    /api/v1/categories/{slug}/posts	Посты категории
POST	/api/v1/auth/register	        Регистрация
POST	/api/v1/auth/login	            Вход
POST	/api/v1/auth/refresh	        Обновление токена

Защищенные endpoints (требуют аутентификации)

Метод	Endpoint	        Описание	                        Роли
GET	    /api/v1/users/me	Информация о текущем пользователе	User+

Админские endpoints (требуют роль Admin)

Метод	Endpoint	                    Описание
GET	    /api/v1/admin/users/	        Список пользователей
PUT	    /api/v1/admin/users/{id}/roles	Обновление ролей пользователя
DELETE	/api/v1/admin/users/{id}	    Деактивация пользователя
POST	/api/v1/admin/posts/	        Создание поста
GET	    /api/v1/admin/posts/	        Список всех постов
PUT	    /api/v1/admin/posts/{id}	    Обновление поста
DELETE	/api/v1/admin/posts/{id}	    Удаление поста
POST	/api/v1/admin/categories/	    Создание категории
GET	    /api/v1/admin/categories/	    Список категорий
PUT	    /api/v1/admin/categories/{id}	Обновление категории
DELETE	/api/v1/admin/categories/{id}	Удаление категории

🧪 Тестирование
```bash
# Запуск всех тестов
pytest

# Запуск тестов с покрытием
pytest --cov=app tests/

# Запуск конкретного модуля тестов
pytest tests/test_services/test_auth_service.py

# Запуск тестов с подробным выводом
pytest -v

# Запуск тестов в Docker
docker-compose exec web pytest
```

🗄 Миграции базы данных
```bash
# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1

# Просмотр текущей версии
alembic current

# Запуск в Docker
docker-compose exec web alembic upgrade head
```

🔧 Скрипты управления
Основные скрипты
```bash
# Запуск приложения (разработка)
python run.py

# Запуск через uvicorn напрямую
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Ожидание готовности базы данных
python scripts/wait_for_db.py

# Заполнение тестовыми данными
python scripts/seed_database.py
└──Пользователи login:password - admin@example.com:1234567q, user@example.com:1234567q
```
Docker команды
```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f web
docker-compose logs -f db

# Пересборка образов
docker-compose build --no-cache

# Выполнение команд в контейнере
docker-compose exec web bash
docker-compose exec db psql -U postgres -d blog_db
```

⚙️ Конфигурация
Основные настройки в файле .env:
```dotenv
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/blog_db

# JWT
SECRET_KEY=change-needed-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12
```

🏗 Архитектура
Проект использует многослойную архитектуру:

1. Models (SQLAlchemy) - работа с базой данных

2. Repositories - абстракция для доступа к данным

3. Services - бизнес-логика

4. Schemas (Pydantic) - валидация данных

5. API Endpoints (FastAPI) - обработка HTTP запросов

Паттерны проектирования
1. Repository Pattern - абстракция доступа к данным

2. Dependency Injection - внедрение зависимостей в FastAPI

3. Service Layer - отделение бизнес-логики от API слоя

📊 База данных
Основные таблицы:
users - пользователи системы
roles - роли и разрешения
user_roles - связь пользователей и ролей
posts - посты блога
categories - категории постов
refresh_tokens - токены обновления

🚢 Production развертывание
Docker Production
```bash
# Сборка production образа
docker build -t blog-backend:latest .

# Запуск с production настройками
docker run -d -p 8000:8000 --env-file .env.production blog-backend:latest
```

Рекомендации для production
- Использовать PostgreSQL в production
- Настроить правильные SECRET_KEY
- Включить HTTPS
- Настроить мониторинг и логирование
- Использовать reverse proxy (nginx)
- Регулярно обновлять зависимости

📝 Планы развития:
- Добавить пагинацию для списков
- Реализовать полнотекстовый поиск
- Добавить загрузку изображений
- Реализовать кэширование (Redis)
- Добавить email уведомления
- Реализовать API для комментариев
- Добавить метрики и аналитику

📄 Лицензия
Open Source

👥 Авторы
Алекандр Суслов (sandrsuslov) - Разработчик