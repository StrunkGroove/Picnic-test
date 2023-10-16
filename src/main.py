import datetime as dt
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import and_
from database import engine, Session, Base, City, User, Picnic, PicnicRegistration
from external_requests import CheckCityExisting, GetWeatherRequest
from models import RegisterUserRequest, UserModel
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

app = FastAPI()


@app.post('/api/v1/city/append/', summary='Append City', description='Добавление города по его названию')
def append_city(city: str = Query(description="Название города", default=None)):
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    check = CheckCityExisting()
    if not check.check_existing(city):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return {'id': city_object.id, 'name': city_object.name, 'weather': city_object.weather}


@app.get('/api/v1/city/info/', summary='Get Cities')
def cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение информации о городе
    """
    
    cities = Session().query(City).filter_by(name=q).all()

    return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]


@app.get('/api/v1/users/list/', summary='')
def users_list(filter: str = Query(description="Сортировка", default=None)):
    """
    Список пользователей
    """
    accept = ['asc', 'desc']
    filter = filter.lower()
    if filter not in accept:
        raise HTTPException(status_code=400, detail=f"Разрешенные значения: {accept}")

    users = Session().query(User).order_by(getattr(User.age, filter)()).all()

    return [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]


@app.post('/api/v1/user/register', summary='CreateUser', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/api/v1/picnic/list/', summary='All Picnics', tags=['picnic'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    """
    s = Session()

    query = s.query(
        Picnic,
        City.name,
    )
    if datetime:
        query = query.filter(Picnic.time == datetime)
    if past:
        query = query.filter(Picnic.time >= dt.datetime.now())
    query = query.join(City, Picnic.city_id == City.id)
    picnics = query.all()

    # FIXME Как сделать за 1 запрос на SQLAlchemy 

    picnic_id = [picnic.id for picnic, cities in picnics]

    users = s.query(PicnicRegistration.user_id, User.name, PicnicRegistration.picnic_id) \
        .join(User, User.id == PicnicRegistration.user_id) \
        .filter(PicnicRegistration.picnic_id.in_(picnic_id)) \
        .all()

    dict = {}
    for id in picnic_id:
        dict[id] = []

    for user_id, user_name, picnic_id in users:
        dict[picnic_id].append({"user_id": user_id, "user_name": user_name})

    return [
        {
            "picnic_id": picnic.id,
            "picnic_date": picnic.time,
            "cities": cities,
            "user_data": dict.get(picnic.id),
        } for picnic, cities in picnics
    ]


@app.post('/api/v1/picnic/add/', summary='Picnic Add', tags=['picnic'])
def picnic_add(city_id: int = None, datetime: dt.datetime = None):
    if city_id is None or datetime is None:
        raise HTTPException(status_code=404, detail=f"Все поля должны быть заполнены!")
    
    s = Session()
    city = s.query(City).filter(City.id == city_id).scalar()

    if city is None:
        raise HTTPException(status_code=404, detail=f"Город с id={city_id} не найден")

    p = Picnic(city_id=city_id, time=datetime)
    s.add(p)
    s.commit()

    return {
        'id': p.id,
        'city': city.name,
        'time': p.time,
    }


@app.post('/api/v1/picnic/register/', summary='Picnic Registration', tags=['picnic'])
def register_to_picnic(name: str = None, city_name: str = None, datetime: dt.datetime = None):
    if name is None or city_name is None or datetime is None:
        raise HTTPException(status_code=422, detail=f"Все поля должны быть заполнены!")

    with Session() as s:

        result = s.query(User.id, User.name) \
            .filter(User.name == name).first()
        if result is None:
            raise HTTPException(status_code=422, detail="Пользователь не найден.")

        user_id, user_name = result

        result = s.query(Picnic.id, City.name, Picnic.time) \
            .filter(and_(
                City.name == city_name,
                Picnic.id == City.id,
                Picnic.time == datetime
            )).first()

        if result is None:
            raise HTTPException(status_code=422, detail="Пикник не найден.")

        picnic_id, city_name, picnic_time = result

        picnic_reg = PicnicRegistration(user_id=user_id, picnic_id=picnic_id)
        s.add(picnic_reg)
        s.commit()

        return {
            'id': picnic_reg.id,
            'picnic_id': picnic_id,
            'user_name': user_name,
            'city_name': city_name,
            'picnic_time': picnic_time,
        }
