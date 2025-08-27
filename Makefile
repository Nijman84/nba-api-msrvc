.PHONY: test build run restart restart-dev stop dbshell

test:
	pytest -q

build:
	docker build -t nba-api-msrvc .

OUTPUT_HOST_DIR := $(PWD)/src/app/output

run:
	@echo "Starting NBA API APP container..."
	mkdir -p "$(PWD)/src/app/output"
	docker run --rm \
	  --name nba-api \
	  --user root \
	  -e BALLDONTLIE_API_KEY=${BALLDONTLIE_API_KEY} \
	  -e WORKERS=1 -e THREADS=8 \
	  -p 8000:8000 \
	  -v "$(PWD)/data:/app/data" \
	  -v "$(PWD)/src/app/output:/app/output" \
	  nba-api-msrvc


restart:
	@echo "Rebuilding and restarting container..."
	-docker stop nba-api
	mkdir -p "$(OUTPUT_HOST_DIR)"
	docker build --no-cache -t nba-api-msrvc .
	$(MAKE) run

nuke:
	@echo "Nuking local DuckDB and restarting container..."
	-rm -f ./data/nba.duckdb
	$(MAKE) restart

# Faster iteration (uses cache)
restart-dev:
	-docker stop nba-api
	docker build -t nba-api-msrvc .
	docker run --rm \
	  --name nba-api \
	  -e BALLDONTLIE_API_KEY=$${BALLDONTLIE_API_KEY} \
	  -e WORKERS=1 -e THREADS=8 \
	  -p 8000:8000 \
	  -v "$$PWD/data:/app/data" \
	  nba-api-msrvc

logs:
	docker logs -f $$(docker ps -q --filter ancestor=nba-api-msrvc | head -n1)

shell:
	docker exec -it $$(docker ps -q --filter ancestor=nba-api-msrvc | head -n1) sh

dbshell:
	@command -v duckdb >/dev/null 2>&1 || { \
		echo "duckdb CLI not found."; \
		echo "Install it with:  brew install duckdb"; \
		exit 127; \
	}
	duckdb ./data/nba.duckdb

stop:
	- docker stop nba-api
