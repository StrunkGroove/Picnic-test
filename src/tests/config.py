import sys
sys.path.insert(0, '/code')

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database.database import Base, get_db

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

DATABASE_URL_TEST = "sqlite:///./test.db"
engine_test = create_engine(DATABASE_URL_TEST, connect_args={"check_same_thread": False})
TestingDBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
Base.metadata.create_all(bind=engine_test)

def override_get_db():
    db = TestingDBSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)