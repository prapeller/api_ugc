MONGO_DOCKER_COMPOSE_LOCAL := -f ../docker/mongo/docker-compose-local.yml
MONGO_DB := mongo_db
POSTGRES_DOCKER_COMPOSE_LOCAL := -f ../docker/postgres/docker-compose-local.yml

build-postgres-loc:
	docker-compose $(POSTGRES_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps

build-mongo-loc:
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps

generate:
	python generate_fake_data.py

etl:
	python etl_from_postgres_to_mongo.py

compare:
	python mongo_vs_postgres.py

down-loc:
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) down
	docker-compose $(POSTGRES_DOCKER_COMPOSE_LOCAL) down

down-v-loc:
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) down -v
	docker-compose $(POSTGRES_DOCKER_COMPOSE_LOCAL) down -v

down-v-mongo-loc:
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) down -v

down-v-postgres-loc:
	docker-compose $(POSTGRES_DOCKER_COMPOSE_LOCAL) down -v
