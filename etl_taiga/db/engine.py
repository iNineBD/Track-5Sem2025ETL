# db/engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
import os

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(bind=engine)
