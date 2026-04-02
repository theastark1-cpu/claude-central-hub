from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.investor import Investor
from app.schemas.investor import InvestorCreate, InvestorUpdate, InvestorResponse

router = APIRouter(prefix="/api/investors", tags=["investors"])


@router.get("", response_model=list[InvestorResponse])
def list_investors(db: Session = Depends(get_db)):
    return db.query(Investor).order_by(Investor.name).all()


@router.post("", response_model=InvestorResponse, status_code=201)
def create_investor(data: InvestorCreate, db: Session = Depends(get_db)):
    investor = Investor(**data.model_dump())
    db.add(investor)
    db.commit()
    db.refresh(investor)
    return investor


@router.get("/{investor_id}", response_model=InvestorResponse)
def get_investor(investor_id: UUID, db: Session = Depends(get_db)):
    investor = db.get(Investor, investor_id)
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    return investor


@router.put("/{investor_id}", response_model=InvestorResponse)
def update_investor(investor_id: UUID, data: InvestorUpdate, db: Session = Depends(get_db)):
    investor = db.get(Investor, investor_id)
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(investor, field, value)
    db.commit()
    db.refresh(investor)
    return investor
