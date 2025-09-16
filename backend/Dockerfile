FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# (Опционально) системные зависимости для сборки некоторых пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Обновляем pip + явный индекс, увеличиваем таймаут
RUN python -m pip install --upgrade pip wheel setuptools && \
    pip install --no-cache-dir --timeout 120 -r requirements.txt -i https://pypi.org/simple

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
