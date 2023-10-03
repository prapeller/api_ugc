import datetime as dt

import pydantic as pd


class UserFilmProgressReadSerializer(pd.BaseModel):
    created_at: dt.datetime
    user_uuid: pd.UUID4
    film_uuid: pd.UUID4
    current_time_sec: int
    total_time_sec: int
