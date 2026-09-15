from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TestModel(Base):
    __tablename__ = "test-model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
