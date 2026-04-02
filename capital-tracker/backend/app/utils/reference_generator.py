from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction_chain import TransactionChain


def generate_reference_code(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"TXN-{year}-"
    count = (
        db.query(func.count(TransactionChain.id))
        .filter(TransactionChain.reference_code.like(f"{prefix}%"))
        .scalar()
    )
    return f"{prefix}{(count + 1):04d}"
