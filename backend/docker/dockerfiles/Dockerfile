FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

WORKDIR /app/

# ===================
FROM base AS builder

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user --upgrade --force-reinstall -r /tmp/requirements.txt

# ===================
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r docker && \
    useradd -m -g docker unprivilegeduser && \
    mkdir -p /home/unprivilegeduser && \
    chown -R unprivilegeduser /home/unprivilegeduser

ENV APP_HOME=/home/unprivilegeduser/shortener
WORKDIR $APP_HOME

COPY --from=builder --chown=unprivilegeduser:docker /root/.local/lib/python3.13/site-packages \
 /home/unprivilegeduser/.local/lib/python3.13/site-packages
COPY --from=builder --chown=unprivilegeduser:docker /root/.local/bin /home/unprivilegeduser/.local/bin

ENV PATH="/home/unprivilegeduser/.local/bin:${PATH}"

COPY --chown=unprivilegeduser:docker . $APP_HOME/

RUN find "${APP_HOME}/scripts" -type f -name "*.sh" -exec chmod 755 {} + || true

USER unprivilegeduser

ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "src.shortener_app"]
