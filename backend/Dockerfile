FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

WORKDIR /app/

# ===================
FROM base as builder

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r /tmp/requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ===================
FROM python:3.11-slim

RUN groupadd -r docker && \
    useradd -m -g docker unprivilegeduser && \
    mkdir -p /home/unprivilegeduser && \
    chown -R unprivilegeduser /home/unprivilegeduser

ENV APP_HOME=/home/unprivilegeduser/shortener
WORKDIR $APP_HOME

COPY --from=builder --chown=unprivilegeduser:docker /root/.local/lib/python3.11/site-packages \
 /home/unprivilegeduser/.local/lib/python3.11/site-packages
COPY --from=builder --chown=unprivilegeduser:docker /root/.local/bin /home/unprivilegeduser/.local/bin

ENV PATH="/home/unprivilegeduser/.local/bin:${PATH}"

COPY --chown=unprivilegeduser:docker . $APP_HOME/

RUN chmod +x $APP_HOME/scripts/**.sh

USER unprivilegeduser