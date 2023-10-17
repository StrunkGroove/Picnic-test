import sys
sys.path.insert(0, '../')

from database.models import User
from database.support_func import append_user
from config import client, TestingDBSession


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

        db.query(User).delete()
        db.commit()


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

    with TestingDBSession() as db:
        db.query(User).delete()
        db.commit()