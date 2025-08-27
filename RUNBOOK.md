# NBA API Service — Runbook

This runbook describes how to operate, monitor, and troubleshoot the NBA API microservice in local/dev environments. It complements the main [README.md](./README.md).

---

## 1. Starting and Stopping the Service

### Start
```bash
make run
```
This will:
- build the Docker image if needed,
- mount `./data` into the container at `/app/data` (for DuckDB storage),
- expose the API at <http://localhost:8000>.

### Stop
```bash
make stop
```

### Restart
```bash
make restart
```

---

## 2. Database Operations

The service writes to DuckDB (`./data/nba.duckdb`).

### Inspect the DB
You must stop the container first (DuckDB locks the file):
```bash
make stop
duckdb ./data/nba.duckdb "SHOW TABLES; SELECT COUNT(*) FROM games;"
make run
```

### Drop / Reset DB
```bash
make nuke
```
This removes the DuckDB file and restarts fresh.

---

## 3. Logging and Monitoring

### Local Logs
All service logs (app + Gunicorn) are printed to stdout. Run to tail container logs:
```bash
docker logs nba-apis
```

### Log Structuring & Aggregation (future improvement)
In production, deploy a sidecar collector (e.g. **Fluent Bit**) to forward stdout logs:
- Configure app to emit JSON structured logs for parsing into Splunk / Elasticsearch.
- to Splunk HEC (via `-o splunk` output), or
- to Elasticsearch (`-o es` output).  

This enables central dashboards, error greps, and SLA monitoring.

---

## 4. Scheduling and SLA

### Manual Hydration
Hydrate a specific date:
```bash
curl "http://localhost:8000/games?date=2023-03-01" >/dev/null
```

### Production Orchestration (future improvement)
In a real environment (e.g. GCP Composer / Airflow):
- Sample dag in `./dags/nba_hydrate_daily.py`
- Daily DAG scheduled for 07:00 UTC
- Retries + backoff on API errors
- SLA of 15 minutes defined; alerts fire if missed

---

## 5. Troubleshooting

### API responds but DB empty
- Ensure `DUCKDB_PATH` is set consistently (`/app/data/nba.duckdb`).
- Confirm the API returned rows for the requested date (BALLDONTLIE sometimes has gaps).

### File lock errors when querying DB
- Stop the container first (`make stop`) before opening DuckDB CLI.

### Empty logs in Splunk/Elastic (future improvement)
- Verify Fluent Bit sidecar has access to container stdout.
- Check authentication tokens / credentials.

---

## 6. Future Enhancements

- **Metrics export** (Prometheus format) for request counts, latencies, errors.
- **Alerting integration** with Slack/Teams for SLA misses.
- **End-to-end DAG** in Composer/Airflow to orchestrate hydration + downstream transforms.
- **CI/CD pipeline** with pytest + docker-compose smoke tests.

---

✦ **Owner:** Data Engineering  
✦ **SLA:** Yesterday’s data available by 07:10 UTC daily  
✦ **Contact:** #data-engineering (Slack)
