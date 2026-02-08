FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

FROM base AS builder

WORKDIR /build

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN pip install --upgrade pip setuptools wheel \
    && pip wheel . -w /wheels


# ===================
FROM python:3.13-slim

RUN groupadd -r docker \
    && useradd -m -g docker unprivilegeduser

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/*

USER unprivilegeduser

ENTRYPOINT ["python", "-m"]
