from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


password: str = '7403439Mb'
db_name: str = 'SPARKS'

SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:{password}@localhost/{db_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
