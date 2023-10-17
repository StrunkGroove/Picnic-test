import sys
sys.path.insert(0, '../')
import datetime as dt

from database.models import User, City, Picnic
from config import client, TestingDBSession


def append_city(town: str):
    data = {
        "name": f"{town}",
    }
    client.post("/api/v1/city/append/", json=data)

def append_user(data: dict):
    client.post("api/v1/users/register/", json=data)

def append_picnic(id: int, datetime: dt.datetime):
    data = {
        "city_id": f"{id}",
        "datetime": f"{datetime}",
    }
    client.post("/api/v1/picnic/add/", json=data)


def test_register_user():
    data = {
        "name": "string",
        "surname": "string",
        "age": 0
    }

    name = data['name']

    response = client.post("api/v1/users/register/", json=data)
    assert response.status_code == 200

    registered_user = response.json()
    assert isinstance(registered_user["id"], int)
    assert registered_user["name"] == name
    assert registered_user["surname"] == data['surname']
    assert registered_user["age"] == data['age']

    with TestingDBSession() as db:
        db_user = db.query(User).filter(User.name == name).first()
        assert db_user is not None
        assert db_user.name == name


def test_get_user_list():
    data = {
        "name": "string",
        "surname": "string",
        "age": 0
    }
    append_user(data)

    def check(filter: str, reverse: bool):
        response = client.get(f"api/v1/users/list/?filter={filter}")
        assert response.status_code == 200
        response_data = response.json()
        for user_data in response_data['users']:
            assert isinstance(user_data, dict)
            assert set(user_data.keys()) == {"id", "name", "surname", "age"}

        ages = [user['age'] for user in response_data['users']]
        assert ages == sorted(ages, reverse=reverse)
        
    check(filter='asc', reverse=False)
    check(filter='desc', reverse=True)

    response = client.get("api/v1/users/list/?filter=qweqw")
    assert response.status_code == 400


def test_append_city():
    data = {
        "city": "Tyumen",
    }
    response = client.post("/api/v1/city/append/", json=data)

    assert response.status_code == 200
    city_response = response.json()
    assert isinstance(city_response['id'], int)
    assert city_response['name'] == data['city']

    with TestingDBSession() as db:
        db_user = db.query(City).filter(City.name == data['city']).first()
        assert db_user is not None
        assert db_user.name == data['city']


def test_get_city_list():
    append_city('Tyumen')
    append_city('Moscow')
    append_city('Omsk')
    append_city('Tomsk')

    response = client.get("/api/v1/city/info/?q=Tyumen")

    assert response.status_code == 200
    response_data = response.json()
    for user_data in response_data['cities']:
        assert isinstance(user_data, dict)
        assert set(user_data.keys()) == {"id", "name", "weather"}


def test_add_picnic():
    append_city('Tyumen')

    data = {
        "city_id": "1",
        "datetime": "2023-10-17T11:47:07.599Z",
    }
    response = client.post("/api/v1/picnic/add/", json=data)

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)
    assert set(response_data.keys()) == {"id", "city", "time"}

    with TestingDBSession() as db:
        db_user = db.query(Picnic).filter(
            Picnic.city_id == data['city_id'], 
        ).first()
        assert db_user is not None


def test_picnic_list():
    append_city('Tyumen')
    append_city('Moscow')
    append_city('Omsc')

    append_picnic('1', '2023-10-17T11:47:07.599Z')
    append_picnic('2', '2023-10-17T11:60:07.599Z')
    append_picnic('3', '2023-10-17T11:00:07.599Z')

    response = client.get("/api/v1/picnic/list/?past=False")
    assert response.status_code == 200
    response_data = response.json()
    items = response_data['picnics']
    assert isinstance(items, list)
    assert len(items) == 0


    response = client.get("/api/v1/picnic/list/")
    assert response.status_code == 200
    response_data = response.json()
    items = response_data['picnics']
    assert isinstance(items, list)
    assert len(items) > 3


def test_picnic_register():
    data_1 = {
        "name": "string1",
        "city_name": "Tyumen",
        "datetime": "2023-10-17T11:47:07.590000",
    }

    append_city(data_1['city_name'])
    append_picnic('1', data_1['datetime'])
    append_user(data_1['name'])

    response = client.post("/api/v1/picnic/register/")
    assert response.status_code == 422

    def test(data):
        response = client.post("/api/v1/picnic/register/", json=data)
        assert response.status_code == 200
        res = response.json()
        assert isinstance(res, dict)
        assert res['user_name'] == data['name']
        assert res['city_name'] == data['city_name']
        assert res['picnic_time'] == data['datetime']
    test(data_1)