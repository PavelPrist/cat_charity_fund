from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt, validator

from app.schemas.base import BaseSchema


class CharityProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    full_amount: PositiveInt

    @validator('name', 'description')
    def none_and_empty_not_allowed(cls, value: str):
        if value is None or value == '' or value.isspace():
            raise ValueError('Поле не должно быть пустым или из пробелов')
        return value

    class Config:
        extra = Extra.forbid


class CharityProjectDB(BaseSchema, CharityProjectCreate):
    pass


class CharityProjectUpdate(CharityProjectCreate):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[PositiveInt]
