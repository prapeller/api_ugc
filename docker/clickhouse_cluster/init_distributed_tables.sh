#!/bin/bash

if [ "$HOSTNAME" = "clickhouse-node1" ]; then
    SQL=""
    while IFS= read -r line; do
        SQL+="$line"
        if [[ "$line" == *";"* ]]; then
            clickhouse-client --host localhost -q "$SQL"
            SQL=""
        fi
    done < /docker-entrypoint-initdb.d/init_distributed_tables.sql
fi