from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"
    id           = Column(Integer, primary_key=True)
    article_id   = Column(String(255), unique=True, nullable=False)
    title        = Column(Text, nullable=False)
    description  = Column(Text)
    content      = Column(Text)
    source       = Column(String(255))
    author       = Column(Text)
    url          = Column(Text)
    image_url    = Column(Text)
    category     = Column(Text)
    language     = Column(String(100))
    country      = Column(Text)
    published_at = Column(TIMESTAMP(timezone=True))


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    id          = Column(Integer, primary_key=True)
    article_id  = Column(String(255))
    summary     = Column(Text)
    sentiment   = Column(String(20))
    insights    = Column(ARRAY(Text))
    analyzed_at = Column(TIMESTAMP(timezone=True))


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id         = Column(Integer, primary_key=True)
    article_id = Column(String(255), unique=True, nullable=False)
    saved_at   = Column(TIMESTAMP(timezone=True), server_default="now()")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
