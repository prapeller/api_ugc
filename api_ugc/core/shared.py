import uuid
from enum import Enum

import pydantic as pd
from bson import ObjectId


def custom_dumps(obj: pd.BaseModel | dict) -> dict:
    if isinstance(obj, pd.BaseModel):
        obj = obj.model_dump()
    for key, value in obj.items():
        if isinstance(value, uuid.UUID):
            obj[key] = str(value)
        elif isinstance(value, ObjectId):
            obj[key] = str(value)
        elif isinstance(value, Enum):
            obj[key] = str(value)
        elif isinstance(value, list):
            for x in value:
                x = custom_dumps(x)
    return obj


def user_likes_dumps(obj: pd.BaseModel | dict) -> dict:
    if isinstance(obj, pd.BaseModel):
        obj = obj.model_dump()
    for key, value in obj.items():
        if isinstance(value, uuid.UUID):
            obj[key] = str(value)
        elif isinstance(value, ObjectId):
            obj[key] = str(value)
    return obj
