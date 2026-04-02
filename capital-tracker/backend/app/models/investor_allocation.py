import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InvestorAllocation(Base):
    __tablename__ = "investor_allocations"
    __table_args__ = (UniqueConstraint("chain_id", "investor_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chain_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transaction_chains.id", ondelete="CASCADE"), nullable=False
    )
    investor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investors.id"), nullable=False)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("entities.id"), nullable=False)
    allocation_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    allocation_pct: Mapped[Decimal | None] = mapped_column(Numeric(7, 4))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    chain = relationship("TransactionChain", back_populates="allocations")
    investor = relationship("Investor", back_populates="allocations")
    source_entity = relationship("Entity", lazy="selectin")
