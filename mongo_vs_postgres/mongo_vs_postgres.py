import datetime

import psycopg2
from pymongo import MongoClient

from config import postgres_settings, mongo_settings

postgres_config = {
    'host': postgres_settings.POSTGRES_HOST,
    'port': postgres_settings.POSTGRES_PORT,
    'dbname': postgres_settings.POSTGRES_DB,
    'user': postgres_settings.POSTGRES_USER,
    'password': postgres_settings.POSTGRES_PASSWORD,
}

if __name__ == '__main__':
    conn = psycopg2.connect(**postgres_config)
    cursor = conn.cursor()

    mongo_client = MongoClient(f'mongodb://{mongo_settings.MONGO_HOST}:{mongo_settings.MONGO_PORT}')
    db = mongo_client[f'{mongo_settings.MONGO_DB}']

    cursor.execute("""
    select uuid from "user" 
    order by random()
    limit 1""")
    user_uuid = cursor.fetchone()[0]

    cursor.execute("""
    select uuid from film 
    order by random()
    limit 1""")
    film_uuid = cursor.fetchone()[0]

    print(f'{user_uuid=:}')
    print(f'{film_uuid=:}')

    queries_postgres = {
        'user_ratings':
            f"SELECT * FROM user_film_rating WHERE user_uuid = '{user_uuid}';",

        'film_comments':
            f"SELECT * FROM user_film_comment WHERE film_uuid = '{film_uuid}';",

        'avg_film_rating':
            f"SELECT AVG(rating) FROM user_film_rating WHERE film_uuid = '{film_uuid}';",

        'film_comments_likes_sums':
            f"""SELECT ufc.comment, SUM(like_value) FROM user_comment_like ucl
                                                    JOIN user_film_comment ufc ON ucl.comment_uuid = ufc.uuid
                                                    WHERE ufc.film_uuid = '{film_uuid}'
                                                    group by ucl.comment_uuid, ufc.comment, ufc.created_at
                                                    order by ufc.created_at
                                                    ;""",

        'user_bookmarks':
            f"SELECT ufb.film_uuid FROM user_film_bookmark ufb WHERE user_uuid = '{user_uuid}';",

        'avg_user_bookmarked_films_ratings':
            f"""SELECT f.title, AVG(ufr.rating) FROM user_film_bookmark ufb 
                                                join user_film_rating ufr 
                                                on ufr.film_uuid = ufb.film_uuid
                                                join film f on f.uuid = ufb.film_uuid
                                                WHERE ufb.user_uuid = '{user_uuid}'
                                                group by f.title;""",
    }

    queries_mongo = {
        'user_ratings': lambda:
        list(db['user_ratings_bookmarks'].find({"user_uuid": user_uuid}, {"film_ratings": 1}))[0]['film_ratings'],

        'film_comments': lambda: list(db['film_comments'].find({"film_uuid": film_uuid}, {"film_comments": 1}))[0][
            'film_comments'],

        'avg_film_rating': lambda: list(db['film_avg_ratings'].find({"film_uuid": film_uuid}, {"avg_rating": 1})),

        'film_comments_likes_sums': lambda: list(db['comment_likes'].find(
            {"comment_uuid": {"$in": [
                comment['comment_uuid'] for comment in
                db['film_comments'].find_one({"film_uuid": film_uuid}, {"film_comments.comment_uuid": 1})[
                    'film_comments']
            ]}},
            {"likes_sum": 1, "_id": 0}
        )),

        'user_bookmarks': lambda: list(
            db['user_ratings_bookmarks'].find({"user_uuid": user_uuid}, {"film_bookmarks": 1}))[0]['film_bookmarks'],

        'avg_user_bookmarked_films_ratings': lambda: list(db['film_avg_ratings'].find({"film_uuid": {
            "$in": [bm['film_uuid'] for bm in
                    db['user_ratings_bookmarks'].find_one({"user_uuid": user_uuid})["film_bookmarks"]]}},
            {"avg_rating": 1}))
    }

    print('')
    print('POSTGRES')
    for query_name, query in queries_postgres.items():
        start = datetime.datetime.now()
        cursor.execute(query)
        results = cursor.fetchall()
        print(f'time: {datetime.datetime.now() - start} sec, {len(results)} {query_name}: {results}')

    print('')
    print('MONGO')
    for query_name, query_func in queries_mongo.items():
        start = datetime.datetime.now()
        results = query_func()
        print(f'time: {datetime.datetime.now() - start} sec, {len(results)} {query_name}: {results}')
