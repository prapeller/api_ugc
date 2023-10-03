import datetime as dt

import pydantic as pd


# "film_comments": [
#     {
#       "film_uuid": "uuid",
#       "film_comments": [
#         {
#           "comment_uuid": "uuid",
#           "created_at": "timestamp",
#           "updated_at": "timestamp",
#           "user_uuid": "uuid",
#           "comment": "string"
#         }
#       ]
#     }
#   ]

class FilmCommentUpdateSerializer(pd.BaseModel):
    comment: str | None = None


class FilmCommentCreateSerializer(pd.BaseModel):
    comment: str
    comment_uuid: pd.UUID4 | None = None
    user_uuid: pd.UUID4 | None = None
    created_at: dt.datetime | None = None


class FilmCommentReadSerializer(pd.BaseModel):
    comment_uuid: pd.UUID4
    created_at: dt.datetime
    updated_at: dt.datetime | None = None
    user_uuid: pd.UUID4
    comment: str


class FilmCommentsReadSerializer(pd.BaseModel):
    film_uuid: pd.UUID4
    film_comments: list[FilmCommentReadSerializer]
