import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.core.db import Base
from src.models.student import Student


metadata = sa.MetaData()


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.now, nullable=True
    )
    students: Mapped[List["Student"]] = relationship(
        secondary="student_course", back_populates="courses"
    )
