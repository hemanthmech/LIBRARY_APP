# ── Stage 1: build dependencies ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps needed to compile some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime system deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project source
COPY . .

# Collect static files at build time
# (SECRET_KEY is a dummy value used only for this build step)
RUN SECRET_KEY=build-time-placeholder \
    DEBUG=False \
    python manage.py collectstatic --noinput

EXPOSE 8000

# Entrypoint: run migrations then start Gunicorn
CMD ["sh", "-c", \
     "python manage.py migrate --noinput && \
      gunicorn library_project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 120"]
