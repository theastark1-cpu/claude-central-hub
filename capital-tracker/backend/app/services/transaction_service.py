from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.transaction_chain import TransactionChain
from app.models.transfer_step import TransferStep
from app.models.investor_allocation import InvestorAllocation
from app.schemas.transaction import (
    ChainCreate,
    ChainDetail,
    StepCreate,
    StepResponse,
    AllocationCreate,
    AllocationResponse,
)
from app.services.audit_service import log_action
from app.utils.reference_generator import generate_reference_code


def _step_to_response(step: TransferStep) -> StepResponse:
    return StepResponse(
        id=step.id,
        chain_id=step.chain_id,
        step_order=step.step_order,
        from_account_id=step.from_account_id,
        from_account_name=step.from_account.name if step.from_account else None,
        from_entity_name=step.from_account.entity.name if step.from_account and step.from_account.entity else None,
        to_account_id=step.to_account_id,
        to_account_name=step.to_account.name if step.to_account else None,
        to_entity_name=step.to_account.entity.name if step.to_account and step.to_account.entity else None,
        amount_sent=step.amount_sent,
        fee=step.fee,
        amount_received=step.amount_received,
        transfer_method=step.transfer_method,
        external_ref=step.external_ref,
        status=step.status,
        initiated_at=step.initiated_at,
        completed_at=step.completed_at,
        notes=step.notes,
    )


def _allocation_to_response(alloc: InvestorAllocation) -> AllocationResponse:
    return AllocationResponse(
        id=alloc.id,
        chain_id=alloc.chain_id,
        investor_id=alloc.investor_id,
        investor_name=alloc.investor.name if alloc.investor else None,
        source_entity_id=alloc.source_entity_id,
        source_entity_name=alloc.source_entity.name if alloc.source_entity else None,
        allocation_amount=alloc.allocation_amount,
        allocation_pct=alloc.allocation_pct,
        notes=alloc.notes,
    )


def _chain_to_detail(chain: TransactionChain) -> ChainDetail:
    return ChainDetail(
        id=chain.id,
        reference_code=chain.reference_code,
        description=chain.description,
        original_amount=chain.original_amount,
        total_fees=chain.total_fees,
        final_amount=chain.final_amount,
        currency=chain.currency,
        source_account_id=chain.source_account_id,
        source_account_name=chain.source_account.name if chain.source_account else None,
        source_entity_name=(
            chain.source_account.entity.name if chain.source_account and chain.source_account.entity else None
        ),
        destination_account_id=chain.destination_account_id,
        destination_account_name=chain.destination_account.name if chain.destination_account else None,
        destination_entity_name=(
            chain.destination_account.entity.name
            if chain.destination_account and chain.destination_account.entity
            else None
        ),
        status=chain.status,
        capital_type=chain.capital_type,
        initiated_at=chain.initiated_at,
        completed_at=chain.completed_at,
        created_at=chain.created_at,
        steps=[_step_to_response(s) for s in chain.steps],
        allocations=[_allocation_to_response(a) for a in chain.allocations],
    )


def create_chain(db: Session, data: ChainCreate) -> ChainDetail:
    ref_code = generate_reference_code(db)

    chain = TransactionChain(
        reference_code=ref_code,
        description=data.description,
        original_amount=data.original_amount,
        currency=data.currency,
        source_account_id=data.source_account_id,
        destination_account_id=data.destination_account_id,
        capital_type=data.capital_type,
    )
    db.add(chain)
    db.flush()

    if data.first_step:
        _add_step_internal(db, chain, data.first_step)

    for alloc_data in data.allocations:
        alloc = InvestorAllocation(
            chain_id=chain.id,
            investor_id=alloc_data.investor_id,
            source_entity_id=alloc_data.source_entity_id,
            allocation_amount=alloc_data.allocation_amount,
            allocation_pct=alloc_data.allocation_pct,
            notes=alloc_data.notes,
        )
        db.add(alloc)

    log_action(db, "transaction_chain", chain.id, "create", new_value=ref_code)
    db.commit()
    db.refresh(chain)
    return _chain_to_detail(chain)


def _add_step_internal(db: Session, chain: TransactionChain, data: StepCreate) -> TransferStep:
    existing_steps = sorted(chain.steps, key=lambda s: s.step_order)
    if existing_steps:
        last_step = existing_steps[-1]
        from_account_id = last_step.to_account_id
        next_order = last_step.step_order + 1
        if data.amount_sent > last_step.amount_received:
            raise HTTPException(
                status_code=400,
                detail=f"Step amount_sent ({data.amount_sent}) exceeds previous step amount_received ({last_step.amount_received})",
            )
    else:
        from_account_id = chain.source_account_id
        next_order = 1

    amount_received = data.amount_sent - data.fee

    step = TransferStep(
        chain_id=chain.id,
        step_order=next_order,
        from_account_id=from_account_id,
        to_account_id=data.to_account_id,
        amount_sent=data.amount_sent,
        fee=data.fee,
        amount_received=amount_received,
        transfer_method=data.transfer_method,
        external_ref=data.external_ref,
        notes=data.notes,
        initiated_at=datetime.now(timezone.utc),
    )
    db.add(step)

    chain.status = "in_transit"
    chain.total_fees = sum(s.fee for s in existing_steps) + data.fee

    return step


def add_step(db: Session, chain_id: UUID, data: StepCreate) -> StepResponse:
    chain = db.get(TransactionChain, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")
    if chain.status in ("completed", "cancelled", "failed"):
        raise HTTPException(status_code=400, detail=f"Cannot add steps to {chain.status} chain")

    step = _add_step_internal(db, chain, data)
    db.flush()
    log_action(db, "transfer_step", step.id, "create", metadata={"chain_id": str(chain_id)})
    db.commit()
    db.refresh(step)
    return _step_to_response(step)


def complete_step(db: Session, chain_id: UUID, step_id: UUID) -> StepResponse:
    chain = db.get(TransactionChain, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    step = db.get(TransferStep, step_id)
    if not step or step.chain_id != chain_id:
        raise HTTPException(status_code=404, detail="Step not found in chain")

    step.status = "completed"
    step.completed_at = datetime.now(timezone.utc)

    log_action(db, "transfer_step", step.id, "update", field_name="status", old_value="pending", new_value="completed")
    db.commit()
    db.refresh(step)
    return _step_to_response(step)


def complete_chain(db: Session, chain_id: UUID) -> ChainDetail:
    chain = db.get(TransactionChain, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    steps = sorted(chain.steps, key=lambda s: s.step_order)
    if not steps:
        raise HTTPException(status_code=400, detail="Cannot complete chain with no steps")

    for s in steps:
        if s.status != "completed":
            s.status = "completed"
            s.completed_at = datetime.now(timezone.utc)

    last_step = steps[-1]
    chain.final_amount = last_step.amount_received
    chain.total_fees = sum(s.fee for s in steps)
    chain.destination_account_id = last_step.to_account_id
    chain.status = "completed"
    chain.completed_at = datetime.now(timezone.utc)

    log_action(
        db,
        "transaction_chain",
        chain.id,
        "complete",
        field_name="status",
        old_value="in_transit",
        new_value="completed",
        metadata={"final_amount": str(chain.final_amount), "total_fees": str(chain.total_fees)},
    )
    db.commit()
    db.refresh(chain)
    return _chain_to_detail(chain)


def get_chain_detail(db: Session, chain_id: UUID) -> ChainDetail:
    chain = db.get(TransactionChain, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")
    return _chain_to_detail(chain)


def list_chains(
    db: Session,
    status: str | None = None,
    capital_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ChainDetail]:
    q = db.query(TransactionChain)
    if status:
        q = q.filter(TransactionChain.status == status)
    if capital_type:
        q = q.filter(TransactionChain.capital_type == capital_type)
    q = q.order_by(TransactionChain.created_at.desc()).offset(offset).limit(limit)
    return [_chain_to_detail(c) for c in q.all()]


def add_allocations(db: Session, chain_id: UUID, allocations: list[AllocationCreate]) -> list[AllocationResponse]:
    chain = db.get(TransactionChain, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    results = []
    for alloc_data in allocations:
        alloc = InvestorAllocation(
            chain_id=chain_id,
            investor_id=alloc_data.investor_id,
            source_entity_id=alloc_data.source_entity_id,
            allocation_amount=alloc_data.allocation_amount,
            allocation_pct=alloc_data.allocation_pct,
            notes=alloc_data.notes,
        )
        db.add(alloc)
        db.flush()
        db.refresh(alloc)
        results.append(_allocation_to_response(alloc))

    log_action(db, "transaction_chain", chain_id, "add_allocations", metadata={"count": len(allocations)})
    db.commit()
    return results
