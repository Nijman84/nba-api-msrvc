# NBA Microservice (Flask + Gunicorn)
#### Author: Neal Hayes `@Nijman84`

## Context
This project was built as part of a Data Engineering technical challenge.  

The brief required a microservice that consumes an NBA API and exposes a REST API to deliver:

1. **List all NBA matches for a given date**
2. **Return data for a single game by game ID**
3. **Download a CSV with aggregated statistics by team** for a date range (median score, % games won, optional home/away split)
4. **Cache data locally** to reduce network traffic

---

## Features
- Flask REST API served by [Gunicorn](https://gunicorn.org/)
- Local caching with [DuckDB](https://duckdb.org/) (`data/nba.duckdb`)
- Data ingestion via [balldontlie.io](https://nba.balldontlie.io/#nba-api) (httpx + retry logic)
- CSV analytics endpoint (median score, win %), with optional home/away breakdown
- Unit tests with `pytest`
- Jupyter notebook for exploratory analysis
- Makefile shortcuts for common tasks

---

## Getting Started

### Pre-requisites
- [Docker Desktop](https://www.docker.com/) installed and running
- A terminal (e.g. [iTerm](https://iterm2.com/))
- A free API key from [Ball Don’t Lie](https://app.balldontlie.io/)

### Run the service
```bash
export BALLDONTLIE_API_KEY=<your_api_key>
BALLDONTLIE_API_KEY=${BALLDONTLIE_API_KEY} make run
```

This builds and runs the container, mounting DuckDB locally.

---

## Endpoints

### 1. Games for a date
```http
GET /games?date=<YYYY-MM-DD>
```

Example:
```bash
curl "http://localhost:8000/games?date=2025-05-10" | jq
```

### 2. Single game
```http
GET /games/<game_id>
```

Example:
```bash
curl "http://localhost:8000/games/18422306" | jq
```

### 3. Aggregated team stats (CSV)
```http
GET /stats/teams.csv?start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>&team=<id|abbr|name|full_name>[&split=home_away]
```

Examples:
```bash
# Boston Celtics by abbreviation
curl "http://localhost:8000/stats/teams.csv?start_date=2025-04-01&end_date=2025-04-30&team=BOS"

# LA Clippers with home/away split
curl "http://localhost:8000/stats/teams.csv?start_date=2025-04-01&end_date=2025-04-30&team=clippers&split=home_away"
```

#### Saving output
```bash
export NBA_TEAM=lakers
export START_DATE=2025-04-01
export END_DATE=2025-04-30
curl -L "http://localhost:8000/stats/teams.csv?start_date=$START_DATE&end_date=$END_DATE&team=$NBA_TEAM&split=home_away"   -o ${NBA_TEAM}_${START_DATE}_${END_DATE}_stats.csv
```

---

## Makefile Commands
- `make build` – build the Docker image  
- `make run` – start the service  
- `make stop` – stop the container  
- `make restart` – rebuild and restart  
- `make nuke` – delete DuckDB + rebuild + restart  
- `make logs` – tail container logs  
- `make shell` – open shell inside container  
- `make dbshell` – open a DuckDB CLI session  

---

## Testing
Run unit tests locally using Python 3.12:

```bash
rm -rf .venv/
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r dev-requirements.txt
pytest
```

Verbosity is controlled via `pytest.ini`.

---

## Project Structure
```
nba-api-msrvc/
├─ notebooks/exploration.ipynb
├─ src/app/
│  ├─ __init__.py
│  ├─ routes.py
│  ├─ services/
│  │  ├─ games_service.py
│  │  └─ stats_service.py
│  ├─ repos/
│  ├─ ingest/
│  └─ infra/
├─ tests/
├─ data/
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ Makefile
└─ README.md
```

---

## Config
- `BALLDONTLIE_API_KEY` (required)
- `DUCKDB_PATH` (default `data/nba.duckdb`)
- `PORT` (default `8000`), `WORKERS` (default `1`)

---

## Future Improvements

This service was designed to be simple and created within a few hours, however, but there are several next steps to improve the app:

- **Richer caching**: persist not just games, but also aggregate stats (e.g. `team_aggregates` table) for faster repeat queries. 
- **CI/CD integration**: GitHub / Bitbucket / Stash with build checks, plug in linter, tests; Integrate with Jenkins for release environments.
- **Observability & Ops**:  
  - Container logs could be aggregated into a centralised system (e.g. Prometheus + Grafana) to monitor errors and performance trends.  
  - A log scraper could forward logs to aggregator Elasticsearch, making it easy to grep for errors and analyse API usage.
- **Security & scaling**:  
  - Kubernetes integration to run multiple containers with load balancing and resilience out of the box.
  - Rate limiting on endpoints to prevent abuse (would be useful on paid subscription).
  - Appropriate credential, secrets and key management software (Secrets Manager (AWS, GCP), Vault (Hashicorp)).
- **Alternative DB choice**:
  - Limited concurrency with Duck DB locally causing access contention.
  - Need a scalable production choice like Big Query in GCP
- **Better API response hygiene**:
  - Custom errors on empty payloads

---
