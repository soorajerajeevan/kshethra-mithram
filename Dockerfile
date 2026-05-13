# Stage 1: Build frontend assets with Node.js
FROM node:18-alpine AS frontend-builder

WORKDIR /build

COPY package*.json ./
COPY webpack.config.js ./
COPY assets ./assets

RUN npm ci && npm run build

# Stage 2: Python runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production \
    APP_VERSION_FILE=/app/.build-version

WORKDIR /app
ARG BUILD_VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Copy built frontend assets from builder stage
COPY --from=frontend-builder /build/app/static/dist ./app/static/dist

RUN BUILD_TAG="${BUILD_VERSION:-$(date -u +%Y.%m.%d-%H%M%S)}" && \
    echo "${BUILD_TAG}" > /app/.build-version

RUN mkdir -p /database /app/app/static/uploads /app/logs

RUN echo '#!/bin/sh\n\
mkdir -p /database\n\
if [ ! -f /database/temple_app.db ]; then\n\
  echo "Initializing database..."\n\
  python run.py seed_data\n\
fi\n\
exec python -m flask run --host=0.0.0.0 --port=5000\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000 || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
