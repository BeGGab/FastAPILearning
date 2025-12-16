import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from src.core.db import Base
from src.core.db import uniq_str_an



metadata = sa.MetaData()


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[uniq_str_an]
    last_name: Mapped[str] = mapped_column(sa.String(50))
    phone_number: Mapped[uniq_str_an]
    bio: Mapped[str] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.utcnow, nullable=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    user: Mapped["User"] = relationship(back_populates="profile")
