from db import Base, engine
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'users'

    __table_args__ = dict(
        extend_existing=True
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    age: int = Column(Integer, nullable=False)


# line to create all tables, if they don't already exist
Base.metadata.create_all(bind=engine)
