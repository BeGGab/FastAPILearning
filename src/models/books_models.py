import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.core.db import Base
from src.core.db import uniq_str_an

metadata = sa.MetaData()


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[List[str]] = mapped_column(sa.String())
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.utcnow, nullable=True
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("authors.id", ondelete="CASCADE"), nullable=False
    )

    author: Mapped["Author"] = relationship(back_populates="books")
