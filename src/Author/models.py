import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.db import Base
from src.db import uniq_str_an




metadata = sa.MetaData()





class Author(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    name: Mapped[str] = mapped_column(sa.String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    books: Mapped[List["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    title: Mapped[List[str]] = mapped_column(sa.String())
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)

    author: Mapped["Author"] = relationship(back_populates="books")


student_course: sa.Table = sa.Table(
    "student_course",
    Base.metadata,
    sa.Column("student_id", sa.ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("course_id", sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)

