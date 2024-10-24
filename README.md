
# MarketplaceAPI

Это приложение представляет собой API для работы с товарами и категориями, написанное на **FastAPI** с использованием **PostgreSQL** в качестве базы данных и **SQLAlchemy** как ORM. Приложение поддерживает фильтрацию товаров по категориям и диапазону цен.

## Функционал

- **CRUD операции** для товаров и категорий.
- Добавление товаров в категории.
- Фильтрация товаров по категориям и диапазону цен.
- Поддержка работы с базой данных PostgreSQL через SQLAlchemy.
- Управление конфигурацией через файл `.env`.
- Возможность развертывания через Docker и Docker Compose.

## Структура проекта

```struct
MarketplaceAPI/
│
├── .env                       # Пример файла с переменными окружения
├── Dockerfile                 # Файл для сборки Docker-образа
├── docker-compose.yml         # Файл для управления контейнерами с помощью Docker Compose
├── main.py                    # Основной файл приложения на FastAPI
├── requirements.txt           # Файл с зависимостями проекта
└── README.md                  # Документация по проекту
```

## Установка и запуск

### 1. Клонирование репозитория

Клонируйте репозиторий с GitHub и перейдите в папку проекта:

```bash
git clone https://github.com/Manabreaker/MarketplaceAPI.git
cd MarketplaceAPI
```

### 2. Настройка переменных окружения

Измените файл `.env` в корне проекта на основе примера и укажите настройки подключения к базе данных. Пример содержания `.env` файла:

```env
POSTGRES_USER=YOUR_USER_NAME_OR_BY_DEFAULT_postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DB=YOUR_DB_NAME
POSTGRES_HOST=YOUR_HOST_OR_BY_DEFAULT_db
POSTGRES_PORT=YOUR_PORT_OR_BY_DEFAULT_5432

DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?client_encoding=utf8
```

### 3. Запуск через Docker

#### Требования:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Запустите проект с помощью Docker Compose:

```bash
docker-compose up --build
```

Проект будет доступен по адресу: `http://localhost:8000`.

Для остановки контейнеров:

```bash
docker-compose down
```

### 4. Запуск локально без Docker

#### Требования:

- **Python 3.10+**
- **PostgreSQL** (для локального запуска необходимо установить PostgreSQL)

#### Шаги:

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Убедитесь, что PostgreSQL запущен, и создайте базу данных. Пример команды для создания базы данных:

```bash
createdb items_db
```

3. Запустите приложение:

```bash
uvicorn main:app --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`.

## API Маршруты

Основные маршруты API:

- `POST /items/` — Создание товара.
- `GET /items/` — Получение списка товаров (с фильтрацией по категориям и цене).
- `PUT /items/{item_id}` — Обновление товара.
- `DELETE /items/{item_id}` — Удаление товара.
- `POST /categories/` — Создание категории.
- `GET /categories/` — Получение списка категорий.
- `POST /categories/{category_id}/items/{item_id}` — Добавление товара в категорию.

Полный список маршрутов можно посмотреть в автоматически сгенерированной документации:

- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
