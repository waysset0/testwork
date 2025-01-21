from sqlalchemy import Column, Integer, String, Float, DateTime, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://testword:123123@db/testwork_database")

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    artikul = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)