from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.entity import Entity
from app.models.investor import Investor
from app.models.investor_allocation import InvestorAllocation
from app.models.transaction_chain import TransactionChain
from app.models.transfer_step import TransferStep
from app.schemas.dashboard import (
    GlobalOverview,
    EntitySummary,
    InvestorSummary,
    AccountSummary,
)


def get_global_overview(db: Session) -> GlobalOverview:
    chains = db.query(TransactionChain).all()

    total_completed = sum(c.final_amount or Decimal("0") for c in chains if c.status == "completed")
    total_in_transit = sum(c.original_amount for c in chains if c.status == "in_transit")
    total_pending = sum(c.original_amount for c in chains if c.status == "pending")
    total_fees = sum(c.total_fees for c in chains)

    return GlobalOverview(
        total_aum_in_motion=total_in_transit + total_pending,
        total_completed=total_completed,
        total_in_transit=total_in_transit,
        total_pending=total_pending,
        total_inflows=total_completed + total_in_transit + total_pending,
        total_outflows=total_completed,
        total_fees_collected=total_fees,
        chain_count_pending=sum(1 for c in chains if c.status == "pending"),
        chain_count_in_transit=sum(1 for c in chains if c.status == "in_transit"),
        chain_count_completed=sum(1 for c in chains if c.status == "completed"),
        chain_count_failed=sum(1 for c in chains if c.status == "failed"),
    )


def get_entity_summaries(db: Session) -> list[EntitySummary]:
    entities = db.query(Entity).all()
    results = []

    for entity in entities:
        account_ids = [a.id for a in entity.accounts]
        if not account_ids:
            results.append(
                EntitySummary(
                    entity_id=entity.id,
                    entity_name=entity.name,
                    total_outgoing=Decimal("0"),
                    total_incoming=Decimal("0"),
                    total_fees=Decimal("0"),
                    chain_count=0,
                )
            )
            continue

        outgoing = (
            db.query(func.coalesce(func.sum(TransferStep.amount_sent), 0))
            .filter(TransferStep.from_account_id.in_(account_ids))
            .scalar()
        )
        incoming = (
            db.query(func.coalesce(func.sum(TransferStep.amount_received), 0))
            .filter(TransferStep.to_account_id.in_(account_ids))
            .scalar()
        )
        fees = (
            db.query(func.coalesce(func.sum(TransferStep.fee), 0))
            .filter(TransferStep.from_account_id.in_(account_ids))
            .scalar()
        )
        chain_count = (
            db.query(func.count(TransactionChain.id.distinct()))
            .filter(TransactionChain.source_account_id.in_(account_ids))
            .scalar()
        )

        results.append(
            EntitySummary(
                entity_id=entity.id,
                entity_name=entity.name,
                total_outgoing=Decimal(str(outgoing)),
                total_incoming=Decimal(str(incoming)),
                total_fees=Decimal(str(fees)),
                chain_count=chain_count or 0,
            )
        )

    return results


def get_investor_summaries(db: Session) -> list[InvestorSummary]:
    investors = db.query(Investor).all()
    results = []

    for inv in investors:
        allocs = db.query(InvestorAllocation).filter(InvestorAllocation.investor_id == inv.id).all()
        if not allocs:
            continue

        total_allocated = sum(a.allocation_amount for a in allocs)
        in_transit = Decimal("0")
        completed = Decimal("0")
        total_fees = Decimal("0")

        for alloc in allocs:
            chain = db.get(TransactionChain, alloc.chain_id)
            if not chain:
                continue
            ratio = alloc.allocation_amount / chain.original_amount if chain.original_amount else Decimal("0")
            if chain.status == "in_transit":
                in_transit += alloc.allocation_amount
            elif chain.status == "completed":
                completed += (chain.final_amount or Decimal("0")) * ratio
            total_fees += chain.total_fees * ratio

        results.append(
            InvestorSummary(
                investor_id=inv.id,
                investor_name=inv.name,
                total_allocated=total_allocated,
                total_in_transit=in_transit,
                total_completed=completed,
                total_fees=total_fees,
                net_received=completed,
            )
        )

    return results


def get_account_summaries(db: Session) -> list[AccountSummary]:
    accounts = db.query(Account).all()
    results = []

    for acct in accounts:
        incoming = (
            db.query(func.coalesce(func.sum(TransferStep.amount_received), 0))
            .filter(TransferStep.to_account_id == acct.id)
            .scalar()
        )
        outgoing = (
            db.query(func.coalesce(func.sum(TransferStep.amount_sent), 0))
            .filter(TransferStep.from_account_id == acct.id)
            .scalar()
        )
        pending_in = (
            db.query(func.coalesce(func.sum(TransferStep.amount_received), 0))
            .filter(TransferStep.to_account_id == acct.id, TransferStep.status == "pending")
            .scalar()
        )
        pending_out = (
            db.query(func.coalesce(func.sum(TransferStep.amount_sent), 0))
            .filter(TransferStep.from_account_id == acct.id, TransferStep.status == "pending")
            .scalar()
        )

        results.append(
            AccountSummary(
                account_id=acct.id,
                account_name=acct.name,
                entity_name=acct.entity.name if acct.entity else "",
                account_type=acct.account_type,
                total_incoming=Decimal(str(incoming)),
                total_outgoing=Decimal(str(outgoing)),
                pending_incoming=Decimal(str(pending_in)),
                pending_outgoing=Decimal(str(pending_out)),
                net_flow=Decimal(str(incoming)) - Decimal(str(outgoing)),
            )
        )

    return results
