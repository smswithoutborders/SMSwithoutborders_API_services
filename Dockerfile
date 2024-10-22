FROM python:3.13.0-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    apache2 \
    apache2-dev \
    python3-dev \
    default-libmysqlclient-dev \
    supervisor \
    libsqlcipher-dev \
    libsqlite3-dev \
    git \
    curl \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /vault

COPY . .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip install -U --quiet --no-cache-dir pip setuptools && \
    pip install --quiet --no-cache-dir --force-reinstall -r requirements.txt && \
    usermod -u 1000 www-data && \
    usermod -G root www-data

FROM base AS development
CMD echo "[*] Starting Development server ..." && \
    make dummy-user-inject && \
    mod_wsgi-express start-server wsgi_script.py \
    --user www-data \
    --group www-data \
    --port '${PORT}' \
    --log-to-terminal

FROM base AS production
ENV MODE=production
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
