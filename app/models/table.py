from __future__ import annotations

from datetime import datetime

from cuid import cuid  # pyright: ignore[reportMissingTypeStubs]
from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Table,
    Text,
    false,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

note_tags = Table(
    "_NoteToTag",
    Base.metadata,
    Column(
        "A",
        Text,
        ForeignKey(
            "Note.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    ),
    Column(
        "B",
        Text,
        ForeignKey(
            "Tag.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    ),
    Index(
        "_NoteToTag_AB_unique",
        "A",
        "B",
        unique=True,
    ),
    Index(
        "_NoteToTag_B_index",
        "B",
    ),
)


class Journal(Base):
    __tablename__ = "Journal"

    title: Mapped[str] = mapped_column(Text)

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user_id: Mapped[str] = mapped_column(
        "userId",
        Text,
    )

    trash: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
    )

    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )

    notes: Mapped[list[Note]] = relationship(
        back_populates="journal",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=cuid,
    )

    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index(
            "Journal_userId_trash_updatedAt_idx",
            "userId",
            "trash",
            "updatedAt",
        ),
    )


class Note(Base):
    __tablename__ = "Note"

    journal_id: Mapped[str] = mapped_column(
        "journalId",
        Text,
        ForeignKey(
            "Journal.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content: Mapped[dict | list | None] = mapped_column(  # type: ignore
        JSONB,
        nullable=True,
    )

    plain_text: Mapped[str | None] = mapped_column(
        "plainText",
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )

    # PostgreSQL:
    # GENERATED ALWAYS AS (...) STORED
    search_vector: Mapped[str | None] = mapped_column(
        "searchVector",
        TSVECTOR,
        Computed(
            """
            setweight(
                to_tsvector(
                    'english'::regconfig,
                    coalesce(title, '')
                ),
                'A'
            )
            ||
            setweight(
                to_tsvector(
                    'english'::regconfig,
                    coalesce("plainText", '')
                ),
                'B'
            )
            """,
            persisted=True,
        ),
        nullable=True,
    )

    journal: Mapped[Journal] = relationship(
        back_populates="notes",
    )

    tags: Mapped[list[Tag]] = relationship(
        secondary=note_tags,
        back_populates="notes",
        passive_deletes=True,
    )

    share: Mapped[NoteShare | None] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=cuid,
    )

    __table_args__ = (
        Index(
            "Note_journalId_createdAt_idx",
            "journalId",
            "createdAt",
        ),
        Index(
            "Note_searchVector_idx",
            "searchVector",
            postgresql_using="gin",
        ),
    )


class NoteShare(Base):
    __tablename__ = "NoteShare"

    token: Mapped[str] = mapped_column(
        Text,
        unique=True,
    )

    note_id: Mapped[str] = mapped_column(
        "noteId",
        Text,
        ForeignKey(
            "Note.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )

    note: Mapped[Note] = relationship(
        back_populates="share",
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=cuid,
    )


class Tag(Base):
    __tablename__ = "Tag"

    name: Mapped[str] = mapped_column(Text)

    user_id: Mapped[str] = mapped_column(
        "userId",
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime,
        server_default=func.now(),
    )

    notes: Mapped[list[Note]] = relationship(
        secondary=note_tags,
        back_populates="tags",
        passive_deletes=True,
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=cuid,
    )

    __table_args__ = (
        Index(
            "Tag_userId_name_key",
            "userId",
            "name",
            unique=True,
        ),
        Index(
            "Tag_userId_name_idx",
            "userId",
            "name",
        ),
    )
