from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.transaction import (
    ChainCreate,
    ChainUpdate,
    ChainDetail,
    StepCreate,
    StepResponse,
    AllocationCreate,
    AllocationResponse,
)
from app.services import transaction_service

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[ChainDetail])
def list_transactions(
    status: str | None = Query(None),
    capital_type: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    return transaction_service.list_chains(db, status=status, capital_type=capital_type, limit=limit, offset=offset)


@router.post("", response_model=ChainDetail, status_code=201)
def create_transaction(data: ChainCreate, db: Session = Depends(get_db)):
    return transaction_service.create_chain(db, data)


@router.get("/{chain_id}", response_model=ChainDetail)
def get_transaction(chain_id: UUID, db: Session = Depends(get_db)):
    return transaction_service.get_chain_detail(db, chain_id)


@router.put("/{chain_id}", response_model=ChainDetail)
def update_transaction(chain_id: UUID, data: ChainUpdate, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    from app.models.transaction_chain import TransactionChain

    chain = db.get(TransactionChain, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")
    if data.description is not None:
        chain.description = data.description
    if data.destination_account_id is not None:
        chain.destination_account_id = data.destination_account_id
    db.commit()
    db.refresh(chain)
    return transaction_service.get_chain_detail(db, chain_id)


@router.post("/{chain_id}/steps", response_model=StepResponse, status_code=201)
def add_step(chain_id: UUID, data: StepCreate, db: Session = Depends(get_db)):
    return transaction_service.add_step(db, chain_id, data)


@router.post("/{chain_id}/steps/{step_id}/complete", response_model=StepResponse)
def complete_step(chain_id: UUID, step_id: UUID, db: Session = Depends(get_db)):
    return transaction_service.complete_step(db, chain_id, step_id)


@router.post("/{chain_id}/complete", response_model=ChainDetail)
def complete_chain(chain_id: UUID, db: Session = Depends(get_db)):
    return transaction_service.complete_chain(db, chain_id)


@router.post("/{chain_id}/allocations", response_model=list[AllocationResponse], status_code=201)
def add_allocations(chain_id: UUID, allocations: list[AllocationCreate], db: Session = Depends(get_db)):
    return transaction_service.add_allocations(db, chain_id, allocations)
