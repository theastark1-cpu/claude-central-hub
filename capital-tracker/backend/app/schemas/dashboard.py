from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class GlobalOverview(BaseModel):
    total_aum_in_motion: Decimal
    total_completed: Decimal
    total_in_transit: Decimal
    total_pending: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    total_fees_collected: Decimal
    chain_count_pending: int
    chain_count_in_transit: int
    chain_count_completed: int
    chain_count_failed: int


class EntitySummary(BaseModel):
    entity_id: UUID
    entity_name: str
    total_outgoing: Decimal
    total_incoming: Decimal
    total_fees: Decimal
    chain_count: int


class InvestorSummary(BaseModel):
    investor_id: UUID
    investor_name: str
    total_allocated: Decimal
    total_in_transit: Decimal
    total_completed: Decimal
    total_fees: Decimal
    net_received: Decimal


class AccountSummary(BaseModel):
    account_id: UUID
    account_name: str
    entity_name: str
    account_type: str
    total_incoming: Decimal
    total_outgoing: Decimal
    pending_incoming: Decimal
    pending_outgoing: Decimal
    net_flow: Decimal
