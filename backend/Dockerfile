FROM python:3.11-slim as base

ARG MODE
ENV \
    # python
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    # poetry
    POETRY_VERSION=1.4.2 \
    POETRY_CACHE_DIR="/var/cache/pypoetry" \
    PATH="/root/.local/bin:$PATH" \
    # curl
    #CURL_VERSION=7.88.1-10+deb12u4 \
    MODE=$MODE

WORKDIR /app/

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    # deps for installing poetry
#        curl=$CURL_VERSION && \
        curl && \
    # install poetry \
    curl -sSL https://install.python-poetry.org | python - --version $POETRY_VERSION && \
    # cleaning cache
    rm -rf /var/cache && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


FROM base as venv

COPY poetry.lock pyproject.toml /app/

RUN \
    # Create requirements.txt from poetry
    poetry config virtualenvs.create false && \
    if [ "$MODE" = "TEST" ]; then \
     poetry export --with dev --format requirements.txt --output /app/requirements.txt --without-hashes; \
    else \
     poetry export --format requirements.txt --output /app/requirements.txt --without-hashes; \
    fi && \
    rm -rf ~/.poetry


FROM python:3.11-slim

RUN \
    # Create group & user
    groupadd -r docker && \
    useradd -m -g docker unprivilegeduser && \
    mkdir -p /home/unprivilegeduser && \
    chown -R unprivilegeduser /home/unprivilegeduser

ENV \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore \
    APP_HOME=/home/unprivilegeduser/shortener

RUN mkdir $APP_HOME

WORKDIR $APP_HOME

COPY --from=venv /app/requirements.txt $APP_HOME/requirements.txt

RUN pip install -r $APP_HOME/requirements.txt --no-cache-dir && \
    rm $APP_HOME/requirements.txt

COPY . $APP_HOME

RUN \
    # add permissions
    chmod +x $APP_HOME/scripts/**.sh && \
    chown -R unprivilegeduser:docker $APP_HOME

USER unprivilegeduser
