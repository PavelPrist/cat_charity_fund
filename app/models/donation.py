from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseModel


class Donation(BaseModel):

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    comment = Column(Text, default=None)
