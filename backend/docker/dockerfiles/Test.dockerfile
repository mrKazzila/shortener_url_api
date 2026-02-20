FROM python:3.13-slim AS builder

WORKDIR /build
RUN pip install --upgrade pip setuptools wheel

COPY pyproject.toml ./
COPY src ./src
RUN pip wheel . -w /wheels


FROM python:3.13-slim

RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/* \
    && pip install --no-cache-dir pytest pytest-asyncio anyio "psycopg[binary]" alembic \
    && rm -rf /wheels

COPY --chown=app:app pyproject.toml /app/pyproject.toml
COPY --chown=app:app alembic.ini /app/alembic.ini
COPY --chown=app:app tests /app/tests
COPY --chown=app:app src/shortener_app/infrastructures/db /app/src/shortener_app/infrastructures/db

USER app
ENTRYPOINT ["python", "-m"]