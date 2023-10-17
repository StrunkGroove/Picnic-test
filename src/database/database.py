import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()

postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_host = os.getenv("POSTGRES_HOST")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()