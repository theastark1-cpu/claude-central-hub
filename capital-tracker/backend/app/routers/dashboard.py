from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import GlobalOverview, EntitySummary, InvestorSummary, AccountSummary
from app.schemas.transaction import ChainDetail
from app.services import dashboard_service, transaction_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=GlobalOverview)
def get_overview(db: Session = Depends(get_db)):
    return dashboard_service.get_global_overview(db)


@router.get("/entities", response_model=list[EntitySummary])
def get_entity_summaries(db: Session = Depends(get_db)):
    return dashboard_service.get_entity_summaries(db)


@router.get("/investors", response_model=list[InvestorSummary])
def get_investor_summaries(db: Session = Depends(get_db)):
    return dashboard_service.get_investor_summaries(db)


@router.get("/accounts", response_model=list[AccountSummary])
def get_account_summaries(db: Session = Depends(get_db)):
    return dashboard_service.get_account_summaries(db)


@router.get("/flow-pipeline", response_model=list[ChainDetail])
def get_flow_pipeline(db: Session = Depends(get_db)):
    return transaction_service.list_chains(db, limit=20)
