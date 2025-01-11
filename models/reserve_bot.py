import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from services.database import create_database_if_not_exists

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_RESERVE")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db(bot):
    create_database_if_not_exists(DATABASE_URL, bot)
    Base.metadata.create_all(engine)
