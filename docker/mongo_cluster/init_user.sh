#!/bin/bash

echo 'use '${MONGO_DB}'
db.createUser({
  user: "'${MONGO_USER}'",
  pwd: "'${MONGO_PASSWORD}'",
  roles: [{ role: "readWrite", db: "'${MONGO_DB}'" }]
})
' | mongosh

MONGO_CONFIG_FILE="/etc/mongod.conf"

# Modify the configuration file to enable authorization
echo "security:
  authorization: enabled" >> "$MONGO_CONFIG_FILE"
