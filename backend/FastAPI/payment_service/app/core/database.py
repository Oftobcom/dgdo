from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# Database engine yaratamiz
engine = create_engine(
    settings.database_url,
    future=True,
    echo=False,
)


# Session factory yaratamiz
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


# Barcha model classlar uchun base class
class Base(DeclarativeBase):
    pass


# Database session dependency
def get_db():

    # Yangi DB session ochamiz
    db = SessionLocal()

    try:
        yield db

    finally:
        # Sessionni yopamiz
        db.close()