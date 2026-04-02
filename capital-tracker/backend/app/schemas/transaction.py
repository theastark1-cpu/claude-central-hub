from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


# --- Transfer Steps ---

class StepCreate(BaseModel):
    to_account_id: UUID
    amount_sent: Decimal
    fee: Decimal = Decimal("0")
    transfer_method: str | None = None
    external_ref: str | None = None
    notes: str | None = None


class StepResponse(BaseModel):
    id: UUID
    chain_id: UUID
    step_order: int
    from_account_id: UUID
    from_account_name: str | None = None
    from_entity_name: str | None = None
    to_account_id: UUID
    to_account_name: str | None = None
    to_entity_name: str | None = None
    amount_sent: Decimal
    fee: Decimal
    amount_received: Decimal
    transfer_method: str | None
    external_ref: str | None
    status: str
    initiated_at: datetime | None
    completed_at: datetime | None
    notes: str | None

    model_config = {"from_attributes": True}


# --- Investor Allocations ---

class AllocationCreate(BaseModel):
    investor_id: UUID
    source_entity_id: UUID
    allocation_amount: Decimal
    allocation_pct: Decimal | None = None
    notes: str | None = None


class AllocationResponse(BaseModel):
    id: UUID
    chain_id: UUID
    investor_id: UUID
    investor_name: str | None = None
    source_entity_id: UUID
    source_entity_name: str | None = None
    allocation_amount: Decimal
    allocation_pct: Decimal | None
    notes: str | None

    model_config = {"from_attributes": True}


# --- Transaction Chains ---

class ChainCreate(BaseModel):
    description: str | None = None
    original_amount: Decimal
    currency: str = "USD"
    source_account_id: UUID
    destination_account_id: UUID | None = None
    capital_type: str
    first_step: StepCreate | None = None
    allocations: list[AllocationCreate] = []


class ChainUpdate(BaseModel):
    description: str | None = None
    destination_account_id: UUID | None = None


class ChainResponse(BaseModel):
    id: UUID
    reference_code: str
    description: str | None
    original_amount: Decimal
    total_fees: Decimal
    final_amount: Decimal | None
    currency: str
    source_account_id: UUID
    source_account_name: str | None = None
    source_entity_name: str | None = None
    destination_account_id: UUID | None
    destination_account_name: str | None = None
    destination_entity_name: str | None = None
    status: str
    capital_type: str
    initiated_at: datetime
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChainDetail(ChainResponse):
    steps: list[StepResponse] = []
    allocations: list[AllocationResponse] = []
