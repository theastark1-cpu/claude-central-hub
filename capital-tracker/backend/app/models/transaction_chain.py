import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TransactionChain(Base):
    __tablename__ = "transaction_chains"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    reference_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    original_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_fees: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    final_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    source_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    destination_account_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("accounts.id"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    capital_type: Mapped[str] = mapped_column(String(30), nullable=False)
    initiated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    source_account = relationship("Account", foreign_keys=[source_account_id], lazy="selectin")
    destination_account = relationship("Account", foreign_keys=[destination_account_id], lazy="selectin")
    steps = relationship(
        "TransferStep",
        back_populates="chain",
        order_by="TransferStep.step_order",
        lazy="selectin",
    )
    allocations = relationship("InvestorAllocation", back_populates="chain", lazy="selectin")
