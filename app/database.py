from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


def get_db():
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]
