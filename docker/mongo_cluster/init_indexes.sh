#!/bin/bash

cmd='
use '${MONGO_DB}'
db.film_comments.createIndex({ "film_uuid": 1 }, { unique: true });
db.film_comments.createIndex({ "film_comments.user_uuid": 1 });
db.film_avg_ratings.createIndex({ "film_uuid": 1 }, { unique: true });
db.comment_likes.createIndex({ "comment_uuid": 1 }, { unique: true });
db.user_ratings_bookmarks.createIndex({ "user_uuid": 1 }, { unique: true });
'

echo "$cmd" | mongosh "mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}"