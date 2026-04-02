from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EntityCreate(BaseModel):
    name: str
    entity_type: str


class EntityUpdate(BaseModel):
    name: str | None = None
    entity_type: str | None = None


class EntityResponse(BaseModel):
    id: UUID
    name: str
    entity_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntityWithAccounts(EntityResponse):
    accounts: list["AccountBrief"] = []


class AccountBrief(BaseModel):
    id: UUID
    name: str
    account_type: str
    provider: str | None

    model_config = {"from_attributes": True}
