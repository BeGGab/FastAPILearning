import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.db import Base
from src.db import uniq_str_an




metadata = sa.MetaData()



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
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    students: Mapped[List["Student"]] = relationship(
        secondary=student_course,
        back_populates="courses"
    )