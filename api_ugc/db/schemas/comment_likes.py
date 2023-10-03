import pydantic as pd

from core.enums import LikeValueEnum


# "comment_likes": [
#     {
#       "comment_uuid": "uuid",
#       "likes_sum": "int",
#       "likes": [
#         {
#           "user_uuid": "uuid",
#           "like_value": "int"
#         }
#       ]
#     }
#   ]

class LikeUpdateSerializer(pd.BaseModel):
    like_value: LikeValueEnum | None = None


class LikeCreateSerializer(pd.BaseModel):
    user_uuid: pd.UUID4 | None = None
    like_value: LikeValueEnum


class LikeReadSerializer(pd.BaseModel):
    user_uuid: pd.UUID4
    like_value: LikeValueEnum


class CommentLikesUpdateSerializer(pd.BaseModel):
    likes_sum: int | None = None
    likes: list[LikeCreateSerializer] = []


class CommentLikesCreateSerializer(pd.BaseModel):
    comment_uuid: pd.UUID4
    likes_sum: int | None = 0
    likes: list[LikeCreateSerializer] = []


class CommentLikesReadSerializer(pd.BaseModel):
    comment_uuid: pd.UUID4
    likes_sum: int
    likes: list[LikeReadSerializer | LikeCreateSerializer] = []
