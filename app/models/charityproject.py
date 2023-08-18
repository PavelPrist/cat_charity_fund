from sqlalchemy import Column, String, Text

from app.models.base import BaseModel


class CharityProject(BaseModel):
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
