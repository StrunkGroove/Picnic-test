import datetime as dt

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import HTTPException
from sqlalchemy import and_

from database.models import Picnic, PicnicRegistration, City, User
from database.database import get_db, DBSession
from schemas.requests import PicnicAddRequest, PicnicRegRequest
from schemas.response import (
    PicnicRegResponse, PicnicAddResponse, UserData, PicnicResponse, 
    PicnicsListResponse
)


router = APIRouter()

@router.get('/list/', summary='All Picnics',
            response_model=PicnicsListResponse)
def all_picnics(datetime: dt.datetime = Query(None, description='Время пикника (по умолчанию не задано)'), 
                past: bool = Query(True, description='Включая уже прошедшие пикники'), 
                db: DBSession = Depends(get_db)):
    """
    Список всех пикников
    """

    query = db.query(
        Picnic,
        City.name,
    )
    if datetime:
        query = query.filter(Picnic.time == datetime)
    if not past:
        query = query.filter(Picnic.time >= dt.datetime.now())
    query = query.join(City, Picnic.city_id == City.id)
    picnics = query.all()

    # FIXME Как сделать за 1 запрос на SQLAlchemy ? inner join ?

    picnic_id = [picnic.id for picnic, cities in picnics]

    users = db.query(PicnicRegistration.user_id, User.name, PicnicRegistration.picnic_id) \
        .join(User, User.id == PicnicRegistration.user_id) \
        .filter(PicnicRegistration.picnic_id.in_(picnic_id)) \
        .all()

    dict = {}
    for id in picnic_id:
        dict[id] = []

    for user_id, user_name, picnic_id in users:
        dict[picnic_id].append(
            UserData(
                user_id=user_id, user_name=user_name
            )
        )

    return PicnicsListResponse(
        picnics=[PicnicResponse(
            picnic_id=picnic.id,
            picnic_date=picnic.time,
            cities=cities,
            user_data=dict.get(picnic.id),
        ) for picnic, cities in picnics]
    )


@router.post('/add/', summary='Picnic Add',
             response_model=PicnicAddResponse)
def picnic_add(request_model: PicnicAddRequest,
               db: DBSession = Depends(get_db)):
    city_id = request_model.city_id
    datetime = request_model.datetime

    if city_id is None or datetime is None:
        raise HTTPException(
            status_code=404,
            detail=f"Все поля должны быть заполнены!"
        )
    
    city = db.query(City).filter(City.id == city_id).scalar()

    if city is None:
        raise HTTPException(
            status_code=404,
            detail=f"Город с id={city_id} не найден"
        )

    p = Picnic(city_id=city_id, time=datetime)
    db.add(p)
    db.commit()

    return PicnicAddResponse(id=p.id, city=city.name, time=p.time)


@router.post('/register/', summary='Picnic Registration',
             response_model=PicnicRegResponse)
def register_to_picnic(request_model: PicnicRegRequest,
                       db: DBSession = Depends(get_db)):
    name = request_model.name
    city_name = request_model.city_name
    datetime = request_model.datetime

    if name is None or city_name is None or datetime is None:
        raise HTTPException(
            status_code=404,
            detail=f"Все поля должны быть заполнены!"
        )

    result = db.query(User.id, User.name) \
        .filter(User.name == name).first()
    if result is None:
        raise HTTPException(
            status_code=405,
            detail="Пользователь не найден."
        )

    user_id, user_name = result

    result = db.query(Picnic.id, City.name, Picnic.time) \
        .filter(and_(
            City.name == city_name,
            Picnic.city_id == City.id,
            Picnic.time == datetime
        )).first()

    if result is None:
        raise HTTPException(
            status_code=406,
            detail="Пикник не найден."
        )

    picnic_id, city_name, picnic_time = result

    picnic_reg = PicnicRegistration(
        user_id=user_id, picnic_id=picnic_id
    )
    db.add(picnic_reg)
    db.commit()

    return PicnicRegResponse(
        id=picnic_reg.id,
        picnic_id=picnic_id,
        user_name=user_name,
        city_name=city_name,
        picnic_time=picnic_time
    )

