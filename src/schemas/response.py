import datetime as dt

from typing import List, Optional
from pydantic import BaseModel


class PicnicRegResponse(BaseModel):
    id: int
    picnic_id: int
    user_name: str
    city_name: str
    picnic_time: dt.datetime

class PicnicAddResponse(BaseModel):
    id: int
    city: str
    time: dt.datetime

class UserData(BaseModel):
    user_id: int
    user_name: str

class PicnicResponse(BaseModel):
    picnic_id: int
    picnic_date: dt.datetime
    cities: str
    user_data: Optional[List[UserData]]

class PicnicsListResponse(BaseModel):
    picnics: List[PicnicResponse]


class UserBaseModel(BaseModel):
    id: int
    name: str
    surname: str
    age: int

class UserModel(UserBaseModel):
    class Config:
        orm_mode = True

class UsersListResponse(BaseModel):
    users: List[UserBaseModel]


class CityBaseModel(BaseModel):
    id: int
    name: str
    weather: str

class CitiesOneResponse(CityBaseModel):
    pass

class CitiesInfoResponse(BaseModel):
    cities: List[CitiesOneResponse]

