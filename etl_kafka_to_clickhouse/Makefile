CLICKHOUSE_COMPOSE_FILE := ../docker/clickhouse/docker-compose.yml
KAFKA_COMPOSE_FILE := ../docker/kafka/docker-compose.yml

build:
	@docker network create shared_network || true
	docker-compose -f $(CLICKHOUSE_COMPOSE_FILE) up --build -d --remove-orphans
	docker-compose -f $(KAFKA_COMPOSE_FILE) up --build -d --remove-orphans

build-clickhouse:
	@docker network create shared_network || true
	docker-compose -f $(CLICKHOUSE_COMPOSE_FILE) up --build -d --remove-orphans --no-deps

build-kafka:
	@docker network create shared_network || true
	docker-compose -f $(KAFKA_COMPOSE_FILE) up --build -d --remove-orphans --no-deps

etl:
	python -m etl.py

down:
	docker-compose -f $(CLICKHOUSE_COMPOSE_FILE) down
	docker-compose -f $(KAFKA_COMPOSE_FILE) down

down-v:
	docker-compose -f $(CLICKHOUSE_COMPOSE_FILE) down -v
	docker-compose -f $(KAFKA_COMPOSE_FILE) down -v