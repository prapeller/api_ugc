MONGO_COMPOSE_FILE := ../docker/mongo/docker-compose.yml
MONGO_CLUSTER_COMPOSE_FILE := ../docker/mongo_cluster/docker-compose.yml
MONGO_DB := mongo_db
POSTGRES_COMPOSE_FILE := ../docker/postgres/docker-compose.yml

build-postgres:
	docker-compose -f $(POSTGRES_COMPOSE_FILE) up --build -d --remove-orphans --no-deps

build-mongo:
	docker-compose -f $(MONGO_COMPOSE_FILE) up --build -d --remove-orphans --no-deps

build-mongo-cluster:
	docker-compose -f $(MONGO_CLUSTER_COMPOSE_FILE) up --build -d --remove-orphans --no-deps

setup-mongo-cluster:
	@echo 'Initializing replica set for config servers...'
	docker exec -it mongo_cfgrs_1 bash -c 'echo "rs.initiate({_id: \"mongo_cfgrs\", configsvr: true, members: [{_id: 0, host: \"mongo_cfgrs_1:27017\"}, {_id: 1, host: \"mongo_cfgrs_2:27017\"}, {_id: 2, host: \"mongo_cfgrs_3:27017\"}]})" | mongosh'

	@echo 'Initializing replica set for shard 1...'
	docker exec -it mongo_rs1_n1 bash -c 'echo "rs.initiate({_id: \"mongo_rs1\", members: [{_id: 0, host: \"mongo_rs1_n1:27017\"}, {_id: 1, host: \"mongo_rs1_n2:27017\"}, {_id: 2, host: \"mongo_rs1_n3:27017\"}]})" | mongosh'

	@echo 'Initializing replica set for shard 2...'
	docker exec -it mongo_rs2_n1 bash -c 'echo "rs.initiate({_id: \"mongo_rs2\", members: [{_id: 0, host: \"mongo_rs2_n1:27017\"}, {_id: 1, host: \"mongo_rs2_n2:27017\"}, {_id: 2, host: \"mongo_rs2_n3:27017\"}]})" | mongosh'

	sleep 10 # Allow replica sets some time to elect a primary

	@echo 'Adding shards to Mongos...'
	docker exec -it mongos_1 bash -c 'echo "sh.addShard(\"mongo_rs1/mongo_rs1_n1:27017,mongo_rs1_n2:27017,mongo_rs1_n3:27017\"); sh.addShard(\"mongo_rs2/mongo_rs2_n1:27017,mongo_rs2_n2:27017,mongo_rs2_n3:27017\");" | mongosh --host mongos_1'

	@echo 'Enable Sharding for Database "$(MONGO_DB)"...'
	docker exec -it mongos_1 bash -c 'echo "sh.enableSharding(\"$(MONGO_DB)\");" | mongosh'
	@echo 'MongoDB cluster setup complete.'

inspect-mongo-cluster-collections:
	@echo "Inspecting MongoDB Collections..."
	@docker cp list_collections.js mongos_1:/tmp/list_collections.js
	@docker exec -it mongos_1 mongosh -f /tmp/list_collections.js

generate:
	python generate_fake_data.py

compare:
	python mongo_vs_postgres.py

down:
	docker-compose -f $(MONGO_CLUSTER_COMPOSE_FILE) down
	docker-compose -f $(MONGO_COMPOSE_FILE) down
	docker-compose -f $(POSTGRES_COMPOSE_FILE) down

down-v:
	docker-compose -f $(MONGO_CLUSTER_COMPOSE_FILE) down -v
	docker-compose -f $(MONGO_COMPOSE_FILE) down -v
	docker-compose -f $(POSTGRES_COMPOSE_FILE) down -v

down-v-mongo:
	docker-compose -f $(MONGO_COMPOSE_FILE) down -v
	docker-compose -f $(MONGO_CLUSTER_COMPOSE_FILE) down -v

down-v-postgres:
	docker-compose -f $(POSTGRES_COMPOSE_FILE) down -v
