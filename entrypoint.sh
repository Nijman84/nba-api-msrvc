#!/bin/sh
set -e

: "${PORT:=8000}"
: "${WORKERS:=1}"          # force single process
: "${THREADS:=8}"          # concurrency via threads

exec gunicorn \
  -k gthread --threads "$THREADS" \
  -w "$WORKERS" -b "0.0.0.0:$PORT" \
  --access-logfile - \
  "src.app:create_app()"
