from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccountCreate(BaseModel):
    entity_id: UUID
    name: str
    account_type: str
    provider: str | None = None
    account_number_last4: str | None = None
    currency: str = "USD"
    is_external: bool = False


class AccountUpdate(BaseModel):
    name: str | None = None
    account_type: str | None = None
    provider: str | None = None
    account_number_last4: str | None = None


class AccountResponse(BaseModel):
    id: UUID
    entity_id: UUID
    name: str
    account_type: str
    provider: str | None
    account_number_last4: str | None
    currency: str
    is_external: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountWithEntity(AccountResponse):
    entity_name: str | None = None
