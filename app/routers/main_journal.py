from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel
from sqlalchemy import desc, false, select
from sqlalchemy.orm import load_only

from app.auth import CurrentUser
from app.database import DbSession
from app.models.table import Journal

router = APIRouter(prefix="/main-journal", tags=["Main Journal"])


class GetAllJournalOut(BaseModel):
    id: str
    title: str
    description: str | None
    user_id: str
    trash: bool
    created_at: datetime
    updated_at: datetime


class CreateJournalIn(BaseModel):
    title: str
    description: str | None = None


class CreateJournalOut(BaseModel):
    id: str


class GetJournalByIdIn(BaseModel):
    id: str


load_only_fields = load_only(
    Journal.id,
    Journal.title,
    Journal.description,
    Journal.user_id,
    Journal.trash,
    Journal.created_at,
    Journal.updated_at,
)


@router.get("/get-all-journal", response_model=list[GetAllJournalOut])
def get_all_journal(db: DbSession, user: CurrentUser):
    data = db.scalars(
        select(Journal)
        .where(Journal.user_id == user)
        .options(load_only_fields)
        .order_by(desc(Journal.updated_at))
    )

    return data


@router.post(
    "/create-journal",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateJournalOut,
)
def create_journal(journal: CreateJournalIn, db: DbSession, user: CurrentUser):
    data = Journal(user_id=user, title=journal.title, description=journal.description)

    db.add(data)
    db.commit()
    db.refresh(data)

    return CreateJournalOut(id=data.id)


@router.get("/get-journal-by-id", response_model=GetAllJournalOut)
def get_journal_by_id(journal: GetJournalByIdIn, db: DbSession, user: CurrentUser):
    stmt = (
        select(Journal)
        .options(load_only_fields)
        .where(
            Journal.id == journal.id, Journal.trash == false(), Journal.user_id == user
        )
    )

    data = db.scalars(stmt).all()

    return data
