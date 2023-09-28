create table if not exists film
(
    id           serial primary key,
    created_at   timestamp default now() not null,
    updated_at   timestamp,
    uuid         uuid unique             not null,
    title        varchar                 not null,
    description  varchar,
    release_date date,
    file_path    varchar,
    "type"       varchar
);


create table if not exists "user"
(
    id         serial primary key,
    created_at timestamp default now() not null,
    updated_at timestamp,
    uuid       uuid unique             not null,
    name       varchar(50),
    email      varchar(50),
    password   varchar(64), -- example length for SHA-256 hash
    is_active  boolean                 not null
);


create table if not exists user_film_rating
(
    id         serial primary key,
    created_at timestamp default now() not null,
    updated_at timestamp,
    user_uuid  uuid references "user"(uuid),
    film_uuid  uuid references film(uuid),
    rating     smallint,
    constraint unique_user_film_rating unique (user_uuid, film_uuid)
);

create table if not exists user_film_comment
(
    id         serial primary key,
    created_at timestamp default now() not null,
    updated_at timestamp,
    uuid       uuid unique             not null,
    user_uuid  uuid references "user"(uuid),
    film_uuid  uuid references film(uuid),
    comment    text
);

create table if not exists user_comment_like
(
    id           serial primary key,
    created_at   timestamp default now() not null,
    updated_at   timestamp,
    user_uuid    uuid references "user"(uuid),
    comment_uuid uuid references user_film_comment(uuid),
    like_value   smallint, -- [ -1 | 0 | 1 ]
    constraint unique_user_comment_like unique (user_uuid, comment_uuid)
);

create table if not exists user_film_bookmark
(
    created_at timestamp default now() not null,
    user_uuid  uuid references "user"(uuid),
    film_uuid  uuid references film(uuid),
    constraint unique_user_film_bookmark unique (user_uuid, film_uuid)
);