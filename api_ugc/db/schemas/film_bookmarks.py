import pydantic as pd


# "user_ratings_bookmarks": [
#     {
#       "user_uuid": "uuid",
#       "film_ratings": [
#         {
#           "film_uuid": "uuid",
#           "rating": "int"
#         }
#       ],
#       "film_bookmarks": [
#         {
#           "film_uuid": "uuid"
#         }
#       ]
#     }
#   ]

class BookmarkSerializer(pd.BaseModel):
    film_uuid: pd.UUID4


class UserBookmarksSerializer(pd.BaseModel):
    user_uuid: pd.UUID4
    film_bookmarks: list[BookmarkSerializer]
