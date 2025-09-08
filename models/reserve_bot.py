from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from services.database import create_database_if_not_exists
from settings import settings

engine = create_engine(settings.DATABASE_URL_RESERVE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db(bot):
    create_database_if_not_exists(settings.DATABASE_URL_RESERVE, bot)
    Base.metadata.create_all(engine)
