import datetime as dt

from config import client


def append_city(town: str) -> None:
    data = {
        "city": town,
    }
    client.post("/api/v1/city/append/", json=data)

def append_user(name: str, years: int) -> None:
    data = {
        "name": name,
        "surname": name,
        "age": years
    }
    client.post("api/v1/users/register/", json=data)

def append_picnic(id: int, datetime: dt.datetime) -> None:
    data = {
        "city_id": id,
        "datetime": datetime,
    }
    client.post("/api/v1/picnic/add/", json=data)