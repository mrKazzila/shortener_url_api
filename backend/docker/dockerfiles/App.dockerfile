FROM python:3.13-slim AS builder

WORKDIR /build

RUN pip install --upgrade pip setuptools wheel

COPY pyproject.toml ./
COPY src ./src

RUN pip wheel . -w /wheels


# ===================
FROM python:3.13-slim

RUN groupadd -r app \
    && useradd -r -g app app

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

USER app

ENTRYPOINT ["python", "-m"]
