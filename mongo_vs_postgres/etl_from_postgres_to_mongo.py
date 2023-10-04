import psycopg2
from faker import Faker
from pymongo import MongoClient

from config import postgres_settings, mongo_settings

fake = Faker()

postgres_config = {
    'host': postgres_settings.POSTGRES_HOST,
    'port': postgres_settings.POSTGRES_PORT,
    'dbname': postgres_settings.POSTGRES_DB,
    'user': postgres_settings.POSTGRES_USER,
    'password': postgres_settings.POSTGRES_PASSWORD,
}


def mongo_insert_film_ratings(cursor, db, batch_size):
    """
     "film_ratings": [
    {
      "film_uuid": "uuid",
      "avg_rating": "float",
      "user_ratings": [
        {
          "user_uuid": "uuid",
          "rating": "int"
        }
      ]
    }
  ]
    """
    if 'film_ratings' not in db.list_collection_names():
        db.create_collection('film_ratings')
    film_ratings_col = db['film_ratings']
    film_ratings_col.delete_many({})

    cursor.execute(f"""
    select ufr.film_uuid, avg(ufr.rating), 
    array_agg(json_build_object('user_uuid', ufr.user_uuid,
                                'rating', ufr.rating)) as user_ratings
    from user_film_rating ufr
    group by ufr.film_uuid
    """)

    while True:
        batch = [{
            'film_uuid': res[0],
            'avg_rating': float(res[1]),
            'user_ratings': (res[2])
        } for res in cursor.fetchmany(batch_size)]
        if not batch:
            break
        print(f'insert_film_ratings {len(batch)}')
        film_ratings_col.insert_many(batch)


def mongo_insert_film_comments(cursor, db, batch_size):
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


def mongo_insert_comment_likes(cursor, db, batch_size):
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


def mongo_insert_user_ratings_bookmarks(cursor, db, batch_size):
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
    conn = psycopg2.connect(**postgres_config)
    cursor = conn.cursor()

    # etl this data to mongo
    mongo_client = MongoClient(f'mongodb://{mongo_settings.MONGO_HOST}:{mongo_settings.MONGO_PORT}')
    db = mongo_client[f'{mongo_settings.MONGO_DB}']

    mongo_insert_comment_likes(cursor, db, batch_size=100000)
    mongo_insert_user_ratings_bookmarks(cursor, db, batch_size=100000)
    mongo_insert_film_ratings(cursor, db, batch_size=1000)
    mongo_insert_film_comments(cursor, db, batch_size=1000)

    cursor.close()
    conn.close()
    mongo_client.close()
