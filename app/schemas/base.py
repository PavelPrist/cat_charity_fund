from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


FROM_TIME = (
    datetime.now() + timedelta(minutes=10)
).isoformat(timespec='minutes', sep='T')

TO_TIME = (
    datetime.now() + timedelta(hours=1)
).isoformat(timespec='minutes', sep='T')


class BaseSchema(BaseModel):
    id: int
    full_amount: PositiveInt
    invested_amount: PositiveInt
    fully_invested: bool
    create_date: datetime = Field(..., example=FROM_TIME)
    close_date: Optional[datetime] = Field(..., example=TO_TIME)

    class Config:
        orm_mode = True
        extra = Extra.forbid
