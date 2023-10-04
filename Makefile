CLICKHOUSE_DOCKER_COMPOSE_LOCAL := -f ./docker/clickhouse/docker-compose-local.yml
KAFKA_DOCKER_COMPOSE_LOCAL := -f ./docker/kafka/docker-compose-local.yml
MONGO_DOCKER_COMPOSE_LOCAL := -f ./docker/mongo/docker-compose-local.yml
MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL := -f ./docker/mongo_cluster/docker-compose-local.yml
API_DOCKER_COMPOSE_LOCAL := -f ./docker/api/docker-compose-local.yml


build-loc:
	docker-compose $(CLICKHOUSE_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans
	docker-compose $(KAFKA_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans
	docker-compose $(API_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans

down-loc:
	docker-compose $(CLICKHOUSE_DOCKER_COMPOSE_LOCAL) down
	docker-compose $(KAFKA_DOCKER_COMPOSE_LOCAL) down
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) down
	docker-compose $(API_DOCKER_COMPOSE_LOCAL) down

build-with-mongo-cluster-loc:
	@docker network create shared_network || true
	docker-compose $(CLICKHOUSE_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans
	docker-compose $(KAFKA_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans
	docker-compose $(MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans
	docker-compose $(API_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans

clickhouse-build-loc:
	@docker network create shared_network || true
	docker-compose $(CLICKHOUSE_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps

clickhouse-down-loc:
	docker-compose $(CLICKHOUSE_DOCKER_COMPOSE_LOCAL) down

clickhouse-down-v-loc:
	docker-compose $(CLICKHOUSE_DOCKER_COMPOSE_LOCAL) down -v

kafka-build-loc:
	@docker network create shared_network || true
	docker-compose $(KAFKA_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps

mongo-build-loc:
	@docker network create shared_network || true
	docker-compose $(MONGO_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps

mongo-cluster-build-loc:
	docker-compose $(MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps

mongo-cluster-setup-loc:
	@echo 'Initializing replica set for config servers...'
	docker exec -it mongo_cfgrs_1 bash -c 'echo "rs.initiate({_id: \"mongo_cfgrs\", configsvr: true, members: [{_id: 0, host: \"mongo_cfgrs_1:27017\"}, {_id: 1, host: \"mongo_cfgrs_2:27017\"}, {_id: 2, host: \"mongo_cfgrs_3:27017\"}]})" | mongosh'

	@echo 'Initializing replica set for shard 1...'
	docker exec -it mongo_rs1_n1 bash -c 'echo "rs.initiate({_id: \"mongo_rs1\", members: [{_id: 0, host: \"mongo_rs1_n1:27017\"}, {_id: 1, host: \"mongo_rs1_n2:27017\"}, {_id: 2, host: \"mongo_rs1_n3:27017\"}]})" | mongosh'

	@echo 'Initializing replica set for shard 2...'
	docker exec -it mongo_rs2_n1 bash -c 'echo "rs.initiate({_id: \"mongo_rs2\", members: [{_id: 0, host: \"mongo_rs2_n1:27017\"}, {_id: 1, host: \"mongo_rs2_n2:27017\"}, {_id: 2, host: \"mongo_rs2_n3:27017\"}]})" | mongosh'

	sleep 10 # Allow replica sets some time to elect a primary

	@echo 'Adding shards to Mongos...'
	docker exec -it mongos_1 bash -c 'echo "sh.addShard(\"mongo_rs1/mongo_rs1_n1:27017,mongo_rs1_n2:27017,mongo_rs1_n3:27017\"); sh.addShard(\"mongo_rs2/mongo_rs2_n1:27017,mongo_rs2_n2:27017,mongo_rs2_n3:27017\");" | mongosh --host mongos_1'

	@echo 'Enable Sharding for Database MONGO_DB...'
	docker exec -it mongos_1 bash /enable_sharding.sh
	@echo 'MongoDB cluster setup complete.'

mongo-cluster-setup-user-loc:
	@echo "Creating MongoDB user..."
	docker exec -it mongos_1 bash init_user.sh
	docker-compose $(MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL) down
	docker-compose $(MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL) up -d

mongo-cluster-setup-indexes:
	@echo "Creating MongoDB indexes..."
	docker exec -it mongos_1 bash /init_indexes.sh

mongo-cluster-inspect-collections:
	@echo "Inspecting MongoDB Collections..."
	docker exec -it mongos_1 mongosh -f /list_collections.js

mongo-cluster-inspect-config-status:
	docker exec -it mongo_cfgrs_1 bash -c 'echo "rs.status()" | mongosh'

mongo-cluster-inspect-rs1-status:
	docker exec -it mongo_rs1_n1 bash -c 'echo "rs.status()" | mongosh'

mongo-cluster-inspect-rs2-status:
	docker exec -it mongo_rs2_n1 bash -c 'echo "rs.status()" | mongosh'

mongo-cluster-inspect-mongos-status:
	docker exec -it mongos_1 bash -c 'echo "sh.status()" | mongosh'


mongo-inspect-collections:
	@echo "Inspecting MongoDB Collections..."
	docker exec -it mongo_ugc mongosh -f /list_collections.js

mongo-cluster-down-loc:
	docker-compose $(MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL) down

mongo-cluster-down-v-loc:
	docker-compose $(MONGO_CLUSTER_DOCKER_COMPOSE_LOCAL) down -v


api-build-loc:
	@docker network create shared_network || true
	docker-compose $(API_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps


api-check-config:
	docker-compose -f docker-compose-prod.yml -p api_ugc config

api-check-config-loc:
	docker-compose -f docker-compose-local.yml -p api_ugc config

api-pipinstall:
	docker-compose -f docker-compose-prod.yml -p api_ugc run --rm api_ugc pip install -r requirements/prod.txt

api-pipinstall-loc:
	docker-compose -f docker-compose-local.yml -p api_ugc run --rm api_ugc pip install -r requirements/local.txt

api-check-logs:
	docker-compose -f docker-compose-prod.yml -p api_ugc logs

api-check-logs-loc:
	docker-compose -f docker-compose-local.yml -p api_ugc logs



POSTGRES_DOCKER_COMPOSE_LOCAL := -f ./docker/postgres/docker-compose-local.yml

postgres-build-loc:
	docker-compose $(POSTGRES_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps


postgres-down-loc:
	docker-compose $(POSTGRES_DOCKER_COMPOSE_LOCAL) down


etl-kafka-clickhouse-build-loc:
	docker-compose $(API_DOCKER_COMPOSE_LOCAL) up --build -d --remove-orphans --no-deps etl_kafka_postgres_ugc

etl-kafka-clickhouse-down-loc:
	docker-compose $(API_DOCKER_COMPOSE_LOCAL) etl_kafka_postgres_ugc down
