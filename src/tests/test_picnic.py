import sys
sys.path.insert(0, '../')
import datetime as dt

from database.models import Picnic, City, User
from database.support_func import append_city, append_user, append_picnic
from config import client, TestingDBSession


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

    with TestingDBSession() as db:
        db.query(Picnic).delete()
        db.commit()


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
    assert len(items) > 2

    with TestingDBSession() as db:
        db.query(City).delete()
        db.query(Picnic).delete()
        db.commit()
    

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

    with TestingDBSession() as db:
        db.query(City).delete()
        db.query(Picnic).delete()
        db.query(User).delete()
        db.commit()