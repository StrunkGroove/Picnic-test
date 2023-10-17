from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import HTTPException

from database.models import City
from database.database import get_db, DBSession
from schemas.requests import CityAppendRequest
from schemas.response import CitiesOneResponse, CitiesInfoResponse
from api.external_requests import CheckCityExisting


router = APIRouter()

@router.post('/append/', summary='Append City', response_model=CitiesOneResponse, description='Добавление города по его названию')
def append_city(request_model: CityAppendRequest, db: DBSession = Depends(get_db)):
    city = request_model.city
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    check = CheckCityExisting()
    if not check.check_existing(city):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = db.query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        db.add(city_object)
        db.commit()

    return CitiesOneResponse(id=city_object.id, name=city_object.name, weather=city_object.weather)


@router.get('/info/', summary='Get Citiy', response_model=CitiesInfoResponse, description='Получение информации о городе')
def cities_list(q: str = Query(None, description="Название города"), db: DBSession = Depends(get_db)):
    """
    Получение информации о городе
    """
    cities = db.query(City).filter_by(name=q).all()

    return CitiesInfoResponse(
        cities=[CitiesOneResponse(
            id=city.id, name=city.name, weather=city.weather
        ) for city in cities]
    ) 
