from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field

from app.schemas.base import BaseSchema


class DonationsDb(BaseSchema):
    comment: Optional[str] = Field(None, min_length=1)
    user_id: int


class DonationCreate(BaseModel):
    full_amount: int = Field(..., ge=1)
    comment: Optional[str] = Field(None, min_length=1)

    class Config:
        extra = Extra.forbid
        orm_mode = True


class DonationDb(DonationCreate):
    id: int
    create_date: datetime


class DonationUserId(DonationCreate):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True
