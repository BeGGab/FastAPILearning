import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.core.db import Base
from src.core.db import uniq_str_an

from src.models.courses_model import Course



metadata = sa.MetaData()


student_course: sa.Table = sa.Table(
    "student_course",
    Base.metadata,
    sa.Column(
        "student_id", sa.ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    ),
    sa.Column(
        "course_id", sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    ),
    extend_existing=True,
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.utcnow, nullable=True
    )

    courses: Mapped[List["Course"]] = relationship(
        secondary=student_course, back_populates="students", passive_deletes=True
    )


