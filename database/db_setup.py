from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bi_platform.db")
engine  = create_engine(DATABASE_URL)
Base    = declarative_base()
Session = sessionmaker(bind=engine)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id         = Column(Integer, primary_key=True)
    filename   = Column(String)
    rows       = Column(Integer)
    columns    = Column(Integer)
    timestamp  = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    __tablename__ = "query_logs"
    id         = Column(Integer, primary_key=True)
    question   = Column(String)
    sql_query  = Column(String)
    timestamp  = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database tables created!")


if __name__ == "__main__":
    init_db()