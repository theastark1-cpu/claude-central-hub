import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReconciliationRecord(Base):
    __tablename__ = "reconciliation_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chain_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("transaction_chains.id"))
    step_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("transfer_steps.id"))
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    discrepancy: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unmatched")
    resolved_by: Mapped[str | None] = mapped_column(String(100))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
