from fastapi import Query
from fastapi import HTTPException
from fastapi import APIRouter

from database.database import Session
from database.models import User
from schemas.requests import RegisterUserRequest
from schemas.response import (
    UserModel, UsersListResponse, 
)


router = APIRouter()

@router.post('/user/register/', summary='Create User', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@router.get('/users/list/', summary='Get Users', response_model=UsersListResponse)
def users_list(filter: str = Query(None, description="Сортировка")):
    """
    Список пользователей
    """
    filter = filter.lower()
    accept = ['asc', 'desc']
    if filter not in accept:
        raise HTTPException(status_code=400, detail=f"Разрешенные значения: {accept}")

    users = Session().query(User).order_by(getattr(User.age, filter)()).all()

    return UsersListResponse(
        users=[UserModel(
            id=user.id, name=user.name, surname=user.surname, age=user.age
        ) for user in users])



