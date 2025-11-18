import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.db import Base
from src.db import uniq_str_an




metadata = sa.MetaData()





class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[uniq_str_an]
    email: Mapped[uniq_str_an]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow, nullable=True)

    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"



class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[uniq_str_an]
    last_name: Mapped[str] = mapped_column(sa.String(50))
    phone_number: Mapped[uniq_str_an]
    bio: Mapped[str] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    user: Mapped["User"] = relationship(back_populates="profile")



class Author(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow, nullable=True)

    books: Mapped[List["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[List[str]] = mapped_column(sa.String())
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow, nullable=True)

    author_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)

    author: Mapped["Author"] = relationship(back_populates="books")


student_course: sa.Table = sa.Table(
    "student_course",
    Base.metadata,
    sa.Column("student_id", sa.ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("course_id", sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow, nullable=True)

    courses: Mapped[List["Course"]] = relationship(
        secondary=student_course,
        back_populates="students",
        passive_deletes=True
    )

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow, nullable=True)
    students: Mapped[List["Student"]] = relationship(
        secondary=student_course,
        back_populates="courses"
    )