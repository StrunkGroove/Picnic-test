import datetime as dt
from fastapi import Query
from typing import List, Optional
from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    name: str
    surname: str
    age: int


# class UserModel(BaseModel):
#     id: int
#     name: str
#     surname: str
#     age: int

#     class Config:
#         orm_mode = True


class PicnicRegResponse(BaseModel):
    id: int
    picnic_id: int
    user_name: str
    city_name: str
    picnic_time: dt.datetime

class PicnicRegRequest(BaseModel):
    name: str = Field(None, description='Имя пикника')
    city_name: str = Field(None, description='Название города')
    datetime: dt.datetime = Field(None, description='Время пикника')


class PicnicAddResponse(BaseModel):
    id: int
    city: str
    time: dt.datetime

class PicnicAddRequest(BaseModel):
    city_id: int = Field(None, description='ID города')
    datetime: dt.datetime = Field(None, description='Время пикника')

class CityAppendRequest(BaseModel):
    city: str = Field(None, description="Название города")



class PicnicsListRequest(BaseModel):
    datetime: dt.datetime = Field(None, description='Время пикника (по умолчанию не задано)')
    past: bool = Field(True, description='Включая уже прошедшие пикники')

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

class UsersListRequest(BaseModel):
    filter: str = Field(None, description="Сортировка")

class UserModel(UserBaseModel):
    class Config:
        orm_mode = True

class UsersListResponse(BaseModel):
    users: List[UserBaseModel]


    


class CityBaseModel(BaseModel):
    id: int
    name: str
    weather: str

class CitiesInfoRequest(BaseModel):
    q: str = Query(None, description="Название города")

class CitiesOneResponse(CityBaseModel):
    pass

class CitiesInfoResponse(BaseModel):
    cities: List[CitiesOneResponse]

