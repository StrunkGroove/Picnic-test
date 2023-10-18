import sys
sys.path.insert(0, '../')

from database.models import City
from support_func import append_city
from config import client, TestingDBSession


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

        db.query(City).delete()
        db.commit()


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

    with TestingDBSession() as db:
        db.query(City).delete()
        db.commit()
