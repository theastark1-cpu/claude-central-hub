from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InvestorCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class InvestorUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class InvestorResponse(BaseModel):
    id: UUID
    name: str
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
