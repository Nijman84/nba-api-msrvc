# syntax=docker/dockerfile:1

# ---- Base image ----
FROM python:3.12-slim

# ---- Environment ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    WORKERS=1 \
    THREADS=8

# ---- System deps (minimal) ----
# build-essential is handy for native wheels (often not needed, but safe)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---- Workdir ----
WORKDIR /app

# ---- Python deps first (better layer caching) ----
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ---- App code & data ----
# Keep bind mounts for /app/data and /app/output at runtime if you want host persistence.
COPY src /app/src
COPY data /app/data

# ---- Entrypoint ----
COPY entrypoint.sh /app/entrypoint.sh
# Normalise line endings (CRLF -> LF) and ensure executable
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# ---- Non-root user ----
RUN useradd -u 10001 -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# ---- Expose & run ----
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
