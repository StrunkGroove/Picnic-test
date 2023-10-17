import datetime as dt

from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    name: str
    surname: str
    age: int


class PicnicAddRequest(BaseModel):
    city_id: int = Field(None, description='ID города')
    datetime: dt.datetime = Field(None, description='Время пикника')

class PicnicRegRequest(BaseModel):
    name: str
    city_name: str
    datetime: dt.datetime
    

class CityAppendRequest(BaseModel):
    city: str = Field(None, description="Название города")

