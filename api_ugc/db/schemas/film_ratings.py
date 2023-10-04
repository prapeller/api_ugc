import pydantic as pd


# "film_ratings": [
#     {
#       "film_uuid": "uuid",
#       "avg_rating": "float",
#       "user_ratings": [
#         {
#           "user_uuid": "uuid",
#           "rating": "int"
#         }
#       ]
#     }
#   ],
#   "user_ratings_bookmarks": [
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

class FilmRatingUpdateSerializer(pd.BaseModel):
    rating: int | None = None


class FilmRatingReadSerializer(pd.BaseModel):
    film_uuid: pd.UUID4
    rating: int


class UserRatingUpdateSerializer(pd.BaseModel):
    rating: int | None = None


class UserRatingReadSerializer(pd.BaseModel):
    user_uuid: pd.UUID4
    rating: int


class FilmRatingsUpdateSerializer(pd.BaseModel):
    avg_rating: float | None = None
    user_ratings: list[UserRatingUpdateSerializer] = []


class FilmRatingsReadSerializer(pd.BaseModel):
    film_uuid: pd.UUID4
    avg_rating: float
    user_ratings: list[UserRatingReadSerializer]
