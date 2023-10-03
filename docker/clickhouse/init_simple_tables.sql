CREATE TABLE IF NOT EXISTS clickhouse_db.user_film_progress
(
    created_at       DateTime DEFAULT now(),
    user_uuid        UUID,
    film_uuid        UUID,
    current_time_sec Int32,
    total_time_sec   Int32
) ENGINE = MergeTree()
      ORDER BY (created_at, user_uuid, film_uuid);
