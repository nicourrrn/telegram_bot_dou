from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=db)
Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    name = Column(String)
    last_vacancy_time = Column(TIMESTAMP)


Base.metadata.create_all(db)
