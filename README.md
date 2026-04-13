# Airports Project

REST API для управления данными авиаперевозок. Позволяет работать с билетами, рейсами, самолётами и аэропортами, а также получать аналитику.

## Быстрый старт

```bash
git clone https://github.com/sasanchezzz/Airports_project.git
cd Airports_project
docker-compose up --build
```

Откройте [http://localhost:8000/docs](http://localhost:8000/docs) для интерактивной документации.

## Требования

- **Docker** и **Docker Compose** — для запуска в контейнерах
- **Python 3.12+** — для локальной разработки

## Переменные окружения

Приложение использует следующие переменные (задаются в `.env` файле или через `docker-compose`):

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `DB_HOST` | Хост базы данных | `db` |
| `DB_PORT` | Порт базы данных | `5432` |
| `DB_NAME` | Имя базы данных | `demo` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `5621` |

## Локальный запуск (без Docker)

```bash
# Установка зависимостей
uv sync

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Запуск тестов

```bash
docker-compose run --rm api pytest
```

Или локально:

```bash
pytest
```

## API Endpoints

Все эндпоинты можно протестировать через [Swagger UI](http://localhost:8000/docs).

Ниже — примеры запросов через `curl`.

### API v1 — Чтение данных

**GET** `/api/v1/aircrafts/{aircraft_code}` — информация о самолёте
```bash
curl http://localhost:8000/api/v1/aircrafts/773
```

**GET** `/api/v1/airports/` — список аэропортов (пагинация)
```bash
# Все аэропорты
curl http://localhost:8000/api/v1/airports/

# Фильтр по городу
curl http://localhost:8000/api/v1/airports/?city=Москва
```

**GET** `/api/v1/boarding_passes/{ticket_no}` — посадочный талон по номеру билета
```bash
curl http://localhost:8000/api/v1/boarding_passes/0005435999483
```

**GET** `/api/v1/flights/` — список рейсов (пагинация)
```bash
# Все рейсы
curl http://localhost:8000/api/v1/flights/

# Фильтр по номеру рейса
curl http://localhost:8000/api/v1/flights/?flight_no=PG0004

# Фильтр по дате отправления и прибытия
curl http://localhost:8000/api/v1/flights/?scheduled_departure=2016-10-04%2008%3A25%3A00&scheduled_arrival=2016-10-04%2009%3A20%3A00&page=1&size=20

# Фильтр по статусу полета
curl http://localhost:8000/api/v1/flights/?status=On%20Time&page=1&size=20
```

**GET** `/api/v1/flights/city_flights` — рейсы с городами вылета/прилёта
```bash
# Фильтр по городу вылета
curl "http://localhost:8000/api/v1/flights/city_flights?departure_city=Москва"

# Фильтр по городу вылета и статусу полета
curl http://localhost:8000/api/v1/flights/city_flights?departure_city=%D0%9A%D1%80%D0%B0%D1%81%D0%BD%D0%BE%D0%B4%D0%B0%D1%80&status=Scheduled&page=1&size=20
```
---

### API v2 — Управление данными

**POST** `/api/v2/aircrafts/add_aircraft` — добавить самолёт
```bash
curl -X POST http://localhost:8000/api/v2/aircrafts/add_aircraft \
  -H "Content-Type: application/json" \
  -d '{
    "aircraft_code": "T20",
    "model": "Ту-204-100",
    "range": 7500
  }'
```

**PATCH** `/api/v2/aircrafts/{aircraft_code}/range` — обновить дальность самолёта
```bash
curl -X PATCH http://localhost:8000/api/v2/aircrafts/773/range \
  -H "Content-Type: application/json" \
  -d '{"range": 12000}'
```

**DELETE** `/api/v2/aircrafts/{aircraft_code}` — удалить самолёт
```bash
curl -X DELETE http://localhost:8000/api/v2/aircrafts/T20
```

**POST** `/api/v2/airports/upsert` — добавить/обновить аэропорты
```bash
curl -X POST http://localhost:8000/api/v2/airports/upsert \
  -H "Content-Type: application/json" \
  -d '[{
    "airport_code": "UKS",
    "airport_name": "Бельбек",
    "city": "Sevastopol",
    "longitude": 44.691944,
    "latitude": 33.574444,
    "timezone": "Europe/Moscow"
  }]'
```

**DELETE** `/api/v2/airports/{airport_code}` — удалить аэропорт
```bash
curl -X DELETE http://localhost:8000/api/v2/airports/UKS
```

**GET** `/api/v2/flights/analytics` — аналитика маршрутов за период
```bash
curl http://localhost:8000/api/v2/flights/analytics?page=1&size=10&date_from=2016-09-01&date_to=2016-10-01
```

**GET** `/api/v2/seats/` — список мест (пагинация)
```bash
# Все места
curl http://localhost:8000/api/v2/seats/

# Фильтр по коду самолёта
curl http://localhost:8000/api/v2/seats/?aircraft_code=773

# Фильтр по категории места
curl http://localhost:8000/api/v2/seats/?fare_conditions=Business&page=1&size=20
```

**POST** `/api/v2/tickets/create_ticket` — создать билет
```bash
curl -X POST http://localhost:8000/api/v2/tickets/create_ticket \
  -H "Content-Type: application/json" \
  -d '{
    "passenger_id": "1234 567890",
    "passenger_name": "IVAN IVANOV",
    "contact_data": {
      "phone": "+79001234567"
    }
  }'
```

**PUT** `/api/v2/tickets/{ticket_no}` — обновить билет
```bash
curl -X PUT http://localhost:8000/api/v2/tickets/0005435999775 \
  -H "Content-Type: application/json" \
  -d '{
    "passenger_id": "3874 936640",
    "passenger_name": "PETR PETROV",
    "contact_data": {
      "email": "petr@example.com",
      "phone": "+79078495567"
    }
  }'
```

**DELETE** `/api/v2/tickets/{ticket_no}` — удалить билет
```bash
curl -X DELETE http://localhost:8000/api/v2/tickets/0005435999775
```

## Структура проекта

```
app/
├── api/          # Роутеры и эндпоинты (v1, v2)
├── config/       # Настройки приложения (pydantic-settings)
├── models/       # SQLAlchemy модели
├── schemas/      # Pydantic схемы валидации
├── tests/        # Тесты
├── db_connection.py  # Подключение к БД
└── main.py       # Точка входа FastAPI
db_init/          # SQL скрипт для инициализации БД
```

## Стек технологий

- **Backend:** Python 3.12, FastAPI, Uvicorn
- **БД:** PostgreSQL, Asyncpg, SQLAlchemy 2.0
- **Валидация:** Pydantic, pydantic-settings
- **Тесты:** Pytest, pytest-asyncio, Testcontainers
- **Инструменты:** Ruff, Black, MyPy, uv
