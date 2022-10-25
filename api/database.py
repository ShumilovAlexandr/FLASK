import os
from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URL'))
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

