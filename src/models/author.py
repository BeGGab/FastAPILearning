import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.core.db import Base


metadata = sa.MetaData()


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.now, nullable=True
    )

    books: Mapped[List["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan", passive_deletes=True
    )
