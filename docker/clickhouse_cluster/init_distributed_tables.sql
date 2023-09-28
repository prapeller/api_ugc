CREATE TABLE IF NOT EXISTS user_film_progress_distributed
(
    created_at       DateTime,
    user_uuid        UUID,
    film_uuid        UUID,
    current_time_sec Int32,
    total_time_sec   Int32
) ENGINE = Distributed(company_cluster, default, user_film_progress, rand());
