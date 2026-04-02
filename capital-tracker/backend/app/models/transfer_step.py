import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Integer, Text, Numeric, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TransferStep(Base):
    __tablename__ = "transfer_steps"
    __table_args__ = (
        UniqueConstraint("chain_id", "step_order"),
        CheckConstraint("amount_received = amount_sent - fee", name="ck_step_amounts"),
        CheckConstraint("fee >= 0", name="ck_fee_positive"),
        CheckConstraint("step_order > 0", name="ck_step_order_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chain_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transaction_chains.id", ondelete="CASCADE"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    from_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    to_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount_sent: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    amount_received: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    transfer_method: Mapped[str | None] = mapped_column(String(50))
    external_ref: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    initiated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    chain = relationship("TransactionChain", back_populates="steps")
    from_account = relationship("Account", foreign_keys=[from_account_id], lazy="selectin")
    to_account = relationship("Account", foreign_keys=[to_account_id], lazy="selectin")
