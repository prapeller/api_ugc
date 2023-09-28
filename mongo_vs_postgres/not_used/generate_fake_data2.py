import psycopg2
from pymongo import MongoClient

from config import postgres_settings

postgres_config = {
    'host': postgres_settings.POSTGRES_HOST,
    'port': postgres_settings.POSTGRES_PORT,
    'dbname': postgres_settings.POSTGRES_DB,
    'user': postgres_settings.POSTGRES_USER,
    'password': postgres_settings.POSTGRES_PASSWORD,
}

conn = psycopg2.connect(**postgres_config)
cursor = conn.cursor()


def mongo_insert_film_comments_ratings(db, batch_size):
    """
     "film_comments_ratings": [
    {
      "film_uuid": "uuid",
      "avg_rating": "float",
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
    if 'film_comments_ratings' not in db.list_collection_names():
        db.create_collection('film_comments_ratings')
    film_comments_ratings_col = db['film_comments_ratings']
    film_comments_ratings_col.delete_many({})

    cursor.execute(f"""
    select 
    coalesce(ufr.film_uuid, ufc.film_uuid) as film_uuid,
    avg(ufr.rating) as avg_rating,
    array_agg(json_build_object('comment_uuid', ufc.uuid,
                                'created_at', ufc.created_at,
                                'updated_at', ufc.updated_at,
                                'user_uuid', ufc.user_uuid,
                                'comment', ufc.comment)) filter (where ufc.uuid is not null) as film_comments
    from 
        user_film_rating ufr
    left join 
        user_film_comment ufc on ufr.film_uuid = ufc.film_uuid
    group by 
    coalesce(ufr.film_uuid, ufc.film_uuid)
    """)

    while True:
        batch = [{
            'film_uuid': res[0],
            'avg_rating': float(res[1]),
            'film_comments': float(res[2])
        } for res in cursor.fetchmany(batch_size)]
        if not batch:
            break
        print(f'film_comments_ratings {len(batch)}')
        film_comments_ratings_col.insert_many(batch)


if __name__ == '__main__':
    mongo_client = MongoClient('mongodb://127.0.0.1:27017')  # or to 2nd mongos (127.0.0.1:27020)
    db = mongo_client['mongo_db']

    mongo_insert_film_comments_ratings(db, batch_size=1000)

    cursor.close()
    conn.close()
