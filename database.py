from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "postgresql://postgres:BratkaIlya2015@localhost:5432/mydatabase"

# Создание двигателя SQLAlchemy
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определение модели User
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    registration_date = Column(DateTime, default=datetime.datetime.utcnow)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)
