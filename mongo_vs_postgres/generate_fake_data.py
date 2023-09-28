import random
import uuid
from datetime import date
from datetime import datetime

import psycopg2
from faker import Faker
from pymongo import MongoClient, ASCENDING

from config import postgres_settings, mongo_settings

fake = Faker()

postgres_config = {
    'host': postgres_settings.POSTGRES_HOST,
    'port': postgres_settings.POSTGRES_PORT,
    'dbname': postgres_settings.POSTGRES_DB,
    'user': postgres_settings.POSTGRES_USER,
    'password': postgres_settings.POSTGRES_PASSWORD,
}

conn = psycopg2.connect(**postgres_config)
cursor = conn.cursor()

USER = 1_000_000
USER_CHUNK = 1_000

FILM = 50_000
FILM_CHUNK = 1_000

USER_FILM_RATING = 10_000_000
USER_FILM_RATING_CHUNK = 1_000

USER_FILM_COMMENT = 15_000_000
USER_FILM_COMMENT_CHUNK = 1_000

USER_COMMENT_LIKE = 100_000_000
USER_COMMENT_LIKE_CHUNK = 1_000

USER_FILM_BOOKMARK = 10_000_000
USER_FILM_BOOKMARK_CHUNK = 10_000


def get_unique_uuids(table, quantity):
    cursor.execute(f'select count(uuid) uuid from {table};')
    table_count = cursor.fetchone()[0]
    if quantity > table_count:
        raise Exception("Requested quantity exceeds available unique UUIDs")
    cursor.execute(f"select distinct uuid from {table} order by random() limit {quantity};")
    return [record[0] for record in cursor.fetchall()]


def get_random_uuids(table, quantity):
    cursor.execute(f"""
    select uuid from {table};
    """)
    all_uuids = [record[0] for record in cursor.fetchall()]
    return random.choices(all_uuids, k=quantity)


def iterable_to_gen(iterable):
    for item in iterable:
        yield item


def insert_users():
    users_chunk = []
    for _ in range(USER // USER_CHUNK):
        for _ in range(USER_CHUNK):
            user_uuid = str(uuid.uuid4())
            users_chunk.append((
                datetime.now(),
                None,
                user_uuid,
                fake.name(),
                fake.email(),
                fake.sha256(),
                random.choice([True, False])
            ))

        cursor.executemany("""
        insert into "user" (created_at, updated_at, uuid, name, email, password, is_active) 
        values (%s, %s, %s, %s, %s, %s, %s)
        """, users_chunk)
        users_chunk.clear()
        conn.commit()


def insert_films():
    films_chunk = []
    for _ in range(FILM // FILM_CHUNK):
        for _ in range(FILM_CHUNK):
            film_uuid = str(uuid.uuid4())
            films_chunk.append((
                datetime.now(),
                None,
                film_uuid,
                fake.company(),
                fake.text(),
                fake.date_between(start_date='-30y', end_date='today'),
                fake.file_path(),
                random.choice(['Comedy', 'Drama', 'Action'])
            ))

        cursor.executemany("""
        insert into film (created_at, updated_at, uuid, title, description, release_date, file_path, "type") values (%s, %s, %s, %s, %s, %s, %s, %s)
        """, films_chunk)
        films_chunk.clear()
        conn.commit()


def unique_pair_gen(table_1, table_2, quantity):
    user_uuids = get_random_uuids(table_1, quantity)
    film_uuids = get_random_uuids(table_2, quantity)

    unique_pairs = set()
    for u, f in zip(user_uuids, film_uuids):
        unique_pairs.add((u, f))

    while len(unique_pairs) < quantity:
        diff = quantity - len(unique_pairs)
        user_uuids_diff = get_random_uuids(table_1, diff)
        film_uuids_diff = get_random_uuids(table_2, diff)
        unique_pairs_diff = set()
        for u, f in zip(user_uuids_diff, film_uuids_diff):
            unique_pairs_diff.add((u, f))
        unique_pairs.update(unique_pairs_diff)

    return iterable_to_gen(unique_pairs)


def insert_user_film_rating():
    user_uuid_film_uuid_gen = unique_pair_gen('"user"', 'film', USER_FILM_RATING)

    ratings_chunk = []
    for _ in range(USER_FILM_RATING // USER_FILM_RATING_CHUNK):
        for _ in range(USER_FILM_RATING_CHUNK):
            user_uuid, film_uuid = next(user_uuid_film_uuid_gen)
            rating = random.randint(1, 10)
            ratings_chunk.append((datetime.now(), None, user_uuid, film_uuid, rating))

        cursor.executemany("""
        insert into user_film_rating (created_at, updated_at, user_uuid, film_uuid, rating) 
        values (%s, %s, %s, %s, %s)
        """, ratings_chunk)
        ratings_chunk.clear()
        conn.commit()
        print(f'insert_user_film_rating() added {USER_FILM_RATING_CHUNK}')


def insert_user_film_comment():
    user_uuid_film_uuid_gen = unique_pair_gen('"user"', 'film', USER_FILM_COMMENT)

    comments_chunk = []
    for _ in range(USER_FILM_COMMENT // USER_FILM_COMMENT_CHUNK):
        for _ in range(USER_FILM_COMMENT_CHUNK):
            uuid_str = str(uuid.uuid4())
            user_uuid, film_uuid = next(user_uuid_film_uuid_gen)
            comment = 'Some comment'
            comments_chunk.append((uuid_str, datetime.now(), None, user_uuid, film_uuid, comment))

        cursor.executemany("""
        insert into user_film_comment (uuid, created_at, updated_at, user_uuid, film_uuid, comment) 
        values (%s, %s, %s, %s, %s, %s)
        """, comments_chunk)
        comments_chunk.clear()
        conn.commit()
        print(f'insert_user_film_comment() added {USER_FILM_COMMENT_CHUNK}')


def insert_user_comment_like_threaded(start, end, user_uuid_comment_uuid_gen):
    print(start)
    likes_chunk = []
    for _ in range(start, end):
        user_uuid, comment_uuid = next(user_uuid_comment_uuid_gen)
        like_value = random.choice([-1, 1])
        likes_chunk.append((datetime.now(), None, user_uuid, comment_uuid, like_value))

    # Create a new connection for this thread
    conn = psycopg2.connect(**postgres_config)
    cursor = conn.cursor()

    cursor.executemany("""
    insert into user_comment_like (created_at, updated_at, user_uuid, comment_uuid, like_value) 
    values (%s, %s, %s, %s, %s)
    """, likes_chunk)

    conn.commit()
    conn.close()


def insert_user_comment_like():
    user_uuid_comment_uuid_gen = unique_pair_gen('"user"', 'user_film_comment', USER_COMMENT_LIKE)

    likes_chunk = []
    for _ in range(USER_COMMENT_LIKE // USER_COMMENT_LIKE_CHUNK):
        for _ in range(USER_COMMENT_LIKE_CHUNK):
            user_uuid, comment_uuid = next(user_uuid_comment_uuid_gen)
            like_value = random.choice([-1, 1])

            likes_chunk.append((datetime.now(), None, user_uuid, comment_uuid, like_value))

        cursor.executemany("""
        insert into user_comment_like (created_at, updated_at, user_uuid, comment_uuid, like_value) 
        values (%s, %s, %s, %s, %s)
        """, likes_chunk)
        likes_chunk.clear()
        conn.commit()
        print(f'insert_user_comment_like() added {USER_COMMENT_LIKE_CHUNK}')


def insert_user_film_bookmark():
    user_uuid_film_uuid_gen = unique_pair_gen('"user"', 'film', USER_FILM_BOOKMARK)

    bookmarks_chunk = []
    for _ in range(USER_FILM_BOOKMARK // USER_FILM_BOOKMARK_CHUNK):
        for _ in range(USER_FILM_BOOKMARK_CHUNK):
            user_uuid, film_uuid = next(user_uuid_film_uuid_gen)
            bookmarks_chunk.append((datetime.now(), user_uuid, film_uuid))

        cursor.executemany("""
        insert into user_film_bookmark (created_at, user_uuid, film_uuid) 
        values (%s, %s, %s)
        """, bookmarks_chunk)
        bookmarks_chunk.clear()
        conn.commit()
        print(f'insert_user_film_bookmark() added {USER_FILM_BOOKMARK_CHUNK}')


def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} not serializable')


def mongo_insert_film_avg_ratings(db, batch_size):
    """
     "film_ratings": [
    {
      "film_uuid": "uuid",
      "avg_rating": "float",
    }
  ]
    """
    if 'film_avg_ratings' not in db.list_collection_names():
        db.create_collection('film_avg_ratings')
    film_avg_ratings_col = db['film_avg_ratings']
    film_avg_ratings_col.delete_many({})

    cursor.execute(f"""
    select ufr.film_uuid, avg(ufr.rating)
    from user_film_rating ufr
    group by ufr.film_uuid
    """)

    while True:
        batch = [{
            'film_uuid': res[0],
            'avg_rating': float(res[1])
        } for res in cursor.fetchmany(batch_size)]
        if not batch:
            break
        print(f'insert_film_ratings {len(batch)}')
        film_avg_ratings_col.insert_many(batch)


def mongo_insert_film_comments(db, batch_size):
    """
     "film_comments": [
    {
      "film_uuid": "uuid",
      "film_comments": [
        {
          "comment_uuid": "uuid",
          "created_at": "timestamp",
          "updated_at": "timestamp",
          "user_uuid": "uuid",
          "comment": "string"
        }
      ]
    }
  ]
    """
    if 'film_comments' not in db.list_collection_names():
        db.create_collection('film_comments')
    film_comments_col = db['film_comments']
    film_comments_col.delete_many({})

    cursor.execute(f"""
    select ufc.film_uuid, 
    array_agg(json_build_object('comment_uuid', ufc.uuid, 
                                'created_at', ufc.created_at,
                                'updated_at', ufc.updated_at,
                                'user_uuid', ufc.user_uuid,
                                'comment', ufc.comment)) as film_comments
    from user_film_comment ufc
    group by ufc.film_uuid
    """)
    while True:
        batch = [{'film_uuid': res[0], 'film_comments': res[1]} for res in cursor.fetchmany(batch_size)]
        if not batch:
            break
        print(f'insert_film_comments {len(batch)}')
        film_comments_col.insert_many(batch)


def mongo_insert_comment_likes(db, batch_size):
    """
     "comment_likes": [
    {
      "comment_uuid": "uuid",
      "likes_sum": "int",
      "likes": [
        {
          "user_uuid": "uuid",
          "like_value": "int"
        }
      ]
    }
  ]
    """
    if 'comment_likes' not in db.list_collection_names():
        db.create_collection('comment_likes')
    comment_likes_col = db['comment_likes']
    comment_likes_col.delete_many({})

    cursor.execute("""
    select comment_uuid, sum(like_value) as likes_sum, 
    array_agg(json_build_object('user_uuid', user_uuid, 
                                'like_value', like_value)) as likes
    from user_comment_like
    group by comment_uuid
    order by comment_uuid
    """)

    while True:
        batch = [{
            'comment_uuid': res[0],
            'likes_sum': res[1],
            'likes': res[2]
        } for res in cursor.fetchmany(batch_size)]
        if not batch:
            break
        print(f'insert_comment_likes {len(batch)}')
        comment_likes_col.insert_many(batch)


def mongo_insert_user_ratings_bookmarks(db, batch_size):
    """
     "user_ratings_bookmarks": [
    {
      "user_uuid": "uuid",
      "film_ratings": [
        {
          "film_uuid": "uuid",
          "rating": "int"
        }
      ],
      "film_bookmarks": [
        {
          "film_uuid": "uuid"
        }
      ]
    }
  ]
    """
    if 'user_ratings_bookmarks' not in db.list_collection_names():
        db.create_collection('user_ratings_bookmarks')
    user_ratings_bookmarks_col = db['user_ratings_bookmarks']
    user_ratings_bookmarks_col.delete_many({})

    cursor.execute("""
    select ufr.user_uuid, film_ratings, film_bookmarks 
    from (select user_uuid, 
            array_agg(json_build_object('film_uuid', film_uuid,
                                        'rating', rating)) as film_ratings
        from user_film_rating
        group by user_uuid) ufr
        
        join
        
        (select user_uuid, 
            array_agg(json_build_object('film_uuid', film_uuid)) as film_bookmarks
        from user_film_bookmark
        group by user_uuid) ufb on ufr.user_uuid = ufb.user_uuid
    """)

    while True:
        batch = [{
            'user_uuid': res[0],
            'film_ratings': res[1],
            'film_bookmarks': res[2],
        } for res in cursor.fetchmany(batch_size)]
        if not batch:
            break
        print(f'insert_user_ratings_bookmarks {len(batch)}')
        user_ratings_bookmarks_col.insert_many(batch)


if __name__ == '__main__':
    # create fake data in postgres
    insert_users()
    insert_films()
    insert_user_film_rating()
    insert_user_film_comment()
    insert_user_comment_like()
    insert_user_film_bookmark()

    # etl this data to mongo
    mongo_client = MongoClient(f'mongodb://{mongo_settings.MONGO_HOST}:{mongo_settings.MONGO_PORT}')
    db = mongo_client[f'{mongo_settings.MONGO_DB}']

    mongo_insert_comment_likes(db, batch_size=100000)
    mongo_insert_user_ratings_bookmarks(db, batch_size=100000)

    mongo_insert_film_avg_ratings(db, batch_size=1000)
    mongo_insert_film_comments(db, batch_size=1000)

    db['film_comments'].create_index([('film_uuid', ASCENDING)], unique=True)
    db['film_comments'].create_index([('film_comments.user_uuid', ASCENDING)])
    db['film_avg_ratings'].create_index([('film_uuid', ASCENDING)], unique=True)
    db['comment_likes'].create_index([('comment_uuid', ASCENDING)], unique=True)
    db['user_ratings_bookmarks'].create_index([('user_uuid', ASCENDING)], unique=True)

    cursor.close()
    conn.close()
