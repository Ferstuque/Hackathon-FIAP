# Estágio 1: Builder
FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/upload-service/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Estágio 2: Runtime
FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app:/app/shared"

# Instala libpq5 para o PostgreSQL se for usar BD relacional aqui futuramente
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

# Segurança: Usuário não-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Copia os modelos compartilhados
COPY shared/ /app/shared/
# Copia o código do Upload Service
COPY services/upload-service/src/ /app/src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]