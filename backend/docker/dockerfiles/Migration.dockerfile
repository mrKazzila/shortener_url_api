FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN pip install --upgrade pip setuptools wheel

COPY pyproject.toml ./
COPY src ./src

RUN pip wheel . -w /wheels

# ===================
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /app app

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY alembic.ini ./alembic.ini
COPY src ./src

RUN pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels

USER app

ENTRYPOINT ["python", "-m", "alembic", "-c", "/app/alembic.ini"]
