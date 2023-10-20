create table if not exists film
(
    id           serial primary key,
    uuid         uuid unique             not null,
    created_at   timestamp default now() not null,
    updated_at   timestamp,
    title        varchar                 not null,
    description  text,
    release_date date,
    file_path    varchar,
    "type"       varchar(10),
    imdb_rating  numeric
);

create index idx_film_title on film (title);
create index idx_film_type on film ("type");

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

create index idx_user_name on "user" (name);
create index idx_user_email on "user" (email);
create index idx_user_is_active on "user" (is_active);

create table if not exists user_film_rating
(
    id         serial primary key,
    created_at timestamp default now() not null,
    updated_at timestamp,
    user_uuid  uuid references "user" (uuid),
    film_uuid  uuid references film (uuid),
    rating     smallint,
    constraint unique_user_film_rating unique (user_uuid, film_uuid)
);

create index idx_user_film_rating_rating on user_film_rating (rating);

create table if not exists user_film_comment
(
    id         serial primary key,
    created_at timestamp default now() not null,
    updated_at timestamp,
    uuid       uuid unique             not null,
    user_uuid  uuid references "user" (uuid),
    film_uuid  uuid references film (uuid),
    comment    text
);

create index idx_user_film_comment_user_uuid on user_film_comment (user_uuid);

create table if not exists user_comment_like
(
    id           serial primary key,
    created_at   timestamp default now() not null,
    updated_at   timestamp,
    user_uuid    uuid references "user" (uuid),
    comment_uuid uuid references user_film_comment (uuid),
    like_value   smallint,                                               -- [ -1 | 1 ]
    constraint unique_comment_user_like unique (comment_uuid, user_uuid) -- also for leftmost filtering by 'comment_uuid'
);

create table if not exists user_film_bookmark
(
    created_at timestamp default now() not null,
    user_uuid  uuid references "user" (uuid),
    film_uuid  uuid references film (uuid),
    constraint unique_user_film_bookmark unique (user_uuid, film_uuid) -- also for leftmost filtering by 'user_uuid'
);
