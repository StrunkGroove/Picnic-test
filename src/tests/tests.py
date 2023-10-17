import sys
sys.path.insert(0, '/code')

from database.models import User
from config import client, TestingDBSession


def test_register_user():
    user_data = {
        "name": "string",
        "surname": "string",
        "age": 0
    }

    name = user_data['name']

    response = client.post("api/v1/users/register/", json=user_data)
    assert response.status_code == 200

    registered_user = response.json()
    assert isinstance(registered_user["id"], int)
    assert registered_user["name"] == name
    assert registered_user["surname"] == user_data['surname']
    assert registered_user["age"] == user_data['age']

    with TestingDBSession() as db:
        db_user = db.query(User).filter(User.username == name).first()
        assert db_user is not None
        assert db_user.username == name