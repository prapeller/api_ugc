FROM clickhouse/clickhouse-server

COPY init_simple_tables.sql /docker-entrypoint-initdb.d/

COPY init_distributed_tables.sql /docker-entrypoint-initdb.d/
COPY init_distributed_tables.sh /docker-entrypoint-initdb.d/