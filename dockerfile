FROM python:3.11-slim as builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/.venv/bin:$PATH"

# Копируем весь проект
COPY . .

# Проверяем наличие alembic
RUN which alembic && echo "✓ Alembic found" || echo "✗ Alembic NOT found"

# Создание пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]