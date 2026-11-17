import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.core.enums import SagaStatus


SAGA_UNIQUE = "uix_saga_requests_kind_request_id"


class SagaRequest(Base):
    __tablename__ = "saga_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    request_id: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    status: Mapped[SagaStatus] = mapped_column(
        sa.Enum(SagaStatus, name="saga_status", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=SagaStatus.PENDING
    )
    result_id: Mapped[uuid.UUID | None] = mapped_column(sa.UUID, nullable=True)
    attempts: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    error: Mapped[str |None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())


    __table_args__ = (
        sa.UniqueConstraint("kind", "request_id", name=SAGA_UNIQUE),
    )