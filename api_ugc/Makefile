CLICKHOUSE_COMPOSE_FILE := ../docker/clickhouse/docker-compose.yml
KAFKA_COMPOSE_FILE := ../docker/kafka/docker-compose.yml
MONGO_COMPOSE_FILE := ../docker/kafka/docker-compose.yml

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


down:
	docker-compose -f $(CLICKHOUSE_COMPOSE_FILE) down
	docker-compose -f $(KAFKA_COMPOSE_FILE) down


down-v:
	docker-compose -f $(CLICKHOUSE_COMPOSE_FILE) down -v
	docker-compose -f $(KAFKA_COMPOSE_FILE) down -v








build-api:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc up --build -d  --remove-orphans --no-deps api_ugc


mongo-cluster-build:
	docker-compose -f docker/mongo/docker-compose.yml up --build -d --remove-orphans --no-deps

mongo-cluster-down-v:
	docker-compose -f docker/mongo/docker-compose.yml -p mongo down -v

mongo-cluster-config:
	docker exec -it mongo_cfgrs_1 bash -c 'echo "rs.initiate({_id: \"mongo_cfgrs\", configsvr: true, members: [{_id: 0, host: \"mongo_cfgrs_1\"}, {_id: 1, host: \"mongo_cfgrs_2\"}, {_id: 2, host: \"mongo_cfgrs_3\"}]})" | mongosh'

mongo-cluster-rs1-init:
	docker exec -it mongo_rs1_n1 bash -c 'echo "rs.initiate({_id: \"mongo_rs1\", members: [{_id: 0, host: \"mongo_rs1_n1\"}, {_id: 1, host: \"mongo_rs1_n2\"}, {_id: 2, host: \"mongo_rs1_n3\"}]})" | mongosh'

mongo-cluster-rs1-route:
	docker exec -it mongos_1 bash -c 'echo "sh.addShard(\"mongo_rs1/mongo_rs1_n1\")" | mongosh'

mongo-cluster-rs2-init:
	docker exec -it mongo_rs2_n1 bash -c 'echo "rs.initiate({_id: \"mongo_rs2\", members: [{_id: 0, host: \"mongo_rs2_n1\"}, {_id: 1, host: \"mongo_rs2_n2\"}, {_id: 2, host: \"mongo_rs2_n3\"}]})" | mongosh'

mongo-cluster-rs2-route:
	docker exec -it mongos_1 bash -c 'echo "sh.addShard(\"mongo_rs2/mongo_rs2_n1\")" | mongosh'

mongo-cluster-config-status:
	docker exec -it mongo_cfgrs_1 bash -c 'echo "rs.status()" | mongosh'

mongo-cluster-rs1-status:
	docker exec -it mongo_rs1_n1 bash -c 'echo "rs.status()" | mongosh'

mongo-cluster-rs2-status:
	docker exec -it mongo_rs2_n1 bash -c 'echo "rs.status()" | mongosh'

mongo-cluster-mongos-status:
	docker exec -it mongos_1 bash -c 'echo "sh.status()" | mongosh'

mongo-cluster-rs1-create-somedb:
	docker exec -it mongo_rs1_n1 bash -c 'echo "use someDb" | mongosh'

mongo-cluster-mongos-enable-sharding-some-db:
	docker exec -it mongos_1 bash -c 'echo "sh.enableSharding(\"someDb\")" | mongosh'

mongo-cluster-mongos-create-somecollection:
	docker exec -it mongos_1 bash -c 'echo "db.createCollection(\"someDb.someCollection\")" | mongosh'

mongo-cluster-mongos-enable-sharding-some-collection:
	docker exec -it mongos_1 bash -c 'echo "sh.shardCollection(\"someDb.someCollection\", {\"someField\": \"hashed\"})" | mongosh'




up:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc up -d

up-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_ugc up -d

down:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc down

down-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_ugc down



build-redis:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc up --build -d  --remove-orphans --no-deps redis_ugc

build-redis-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_ugc up --build -d  --remove-orphans --no-deps redis_ugc


check-config:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc config

check-config-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_ugc config



pipinstall:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc run --rm api_ugc pip install -r requirements/prod.txt

pipinstall-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_ugc run --rm api_ugc pip install -r requirements/local.txt


check-logs:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_ugc logs

check-logs-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_ugc logs