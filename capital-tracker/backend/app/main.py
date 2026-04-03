from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.routers import entities, accounts, investors, transactions, dashboard, audit


def seed_if_empty():
    """Auto-seed the database on first run."""
    from app.models import Entity, Account, Investor, TransactionChain, TransferStep, InvestorAllocation
    from decimal import Decimal

    db = SessionLocal()
    try:
        if db.query(Entity).first():
            return  # Already seeded

        armada_prime = Entity(name="Armada Prime LLP", entity_type="llp")
        armada_capital = Entity(name="Armada Capital Group LLP", entity_type="llp")
        royal_kks = Entity(name="Royal KKS", entity_type="group")
        cascade = Entity(name="Cascade", entity_type="group")
        external = Entity(name="External", entity_type="external")
        for e in [armada_prime, armada_capital, royal_kks, cascade, external]:
            db.add(e)
        db.flush()

        ap_brokerage = Account(entity_id=armada_prime.id, name="Armada Prime Brokerage", account_type="brokerage", provider="Catalyst")
        ap_bank = Account(entity_id=armada_prime.id, name="Armada Prime Bank", account_type="bank", provider="Grasshopper", account_number_last4="4521")
        ap_wallet = Account(entity_id=armada_prime.id, name="Armada Prime Trust Wallet", account_type="crypto", provider="Trust Wallet")
        ac_bank = Account(entity_id=armada_capital.id, name="Armada Capital Bank", account_type="bank", provider="Grasshopper", account_number_last4="8832")
        ac_brokerage = Account(entity_id=armada_capital.id, name="Armada Capital Brokerage", account_type="brokerage", provider="Catalyst")
        ac_wallet = Account(entity_id=armada_capital.id, name="Armada Capital Trust Wallet", account_type="crypto", provider="Trust Wallet")
        rkks_coinbase = Account(entity_id=royal_kks.id, name="Royal KKS Coinbase", account_type="crypto", provider="Coinbase")
        rkks_bank = Account(entity_id=royal_kks.id, name="Royal KKS Bank", account_type="bank", provider="Wells Fargo")
        cascade_tw = Account(entity_id=cascade.id, name="Cascade Trust Wallet", account_type="crypto", provider="Trust Wallet")
        ext_recipient = Account(entity_id=external.id, name="External Recipient", account_type="bank", is_external=True)
        for a in [ap_brokerage, ap_bank, ap_wallet, ac_bank, ac_brokerage, ac_wallet, rkks_coinbase, rkks_bank, cascade_tw, ext_recipient]:
            db.add(a)
        db.flush()

        investors_list = [
            Investor(name="Lyman Phillips", email="lyman@example.com"),
            Investor(name="Philip Okala", email="pokala@example.com"),
            Investor(name="NC Opportunity Fund, LP"),
            Investor(name="Sarah Martinez", email="smartinez@example.com"),
            Investor(name="David Chen", email="dchen@example.com"),
            Investor(name="Apex Holdings LLC"),
            Investor(name="Robert Williams", email="rwilliams@example.com"),
            Investor(name="Jennifer Park", email="jpark@example.com"),
        ]
        for inv in investors_list:
            db.add(inv)
        db.flush()

        lyman = investors_list[0]
        philip = investors_list[1]

        # Completed chain: Lyman Phillips $106k flow
        chain = TransactionChain(
            reference_code="TXN-2026-0001",
            description="Lyman Phillips withdrawal - Brokerage to external via crypto",
            original_amount=Decimal("106000.00"), currency="USD",
            source_account_id=ap_brokerage.id, destination_account_id=ext_recipient.id,
            capital_type="lp_capital", status="completed",
            total_fees=Decimal("5.00"), final_amount=Decimal("105995.00"),
        )
        db.add(chain)
        db.flush()

        for s in [
            TransferStep(chain_id=chain.id, step_order=1, from_account_id=ap_brokerage.id, to_account_id=ap_bank.id,
                         amount_sent=Decimal("106000.00"), fee=Decimal("2.00"), amount_received=Decimal("105998.00"),
                         transfer_method="wire", status="completed"),
            TransferStep(chain_id=chain.id, step_order=2, from_account_id=ap_bank.id, to_account_id=ap_wallet.id,
                         amount_sent=Decimal("105998.00"), fee=Decimal("3.00"), amount_received=Decimal("105995.00"),
                         transfer_method="ach", status="completed"),
            TransferStep(chain_id=chain.id, step_order=3, from_account_id=ap_wallet.id, to_account_id=ext_recipient.id,
                         amount_sent=Decimal("105995.00"), fee=Decimal("0.00"), amount_received=Decimal("105995.00"),
                         transfer_method="blockchain", status="completed"),
        ]:
            db.add(s)
        db.flush()

        db.add(InvestorAllocation(chain_id=chain.id, investor_id=lyman.id, source_entity_id=armada_prime.id,
                                  allocation_amount=Decimal("106000.00"), allocation_pct=Decimal("100.0000")))

        # In-transit chain: Split transaction
        chain2 = TransactionChain(
            reference_code="TXN-2026-0002",
            description="Split withdrawal - Lyman Phillips + Armada Capital allocation",
            original_amount=Decimal("150000.00"), currency="USD",
            source_account_id=ap_brokerage.id, capital_type="lp_capital",
            status="in_transit", total_fees=Decimal("15.00"),
        )
        db.add(chain2)
        db.flush()

        db.add(TransferStep(chain_id=chain2.id, step_order=1, from_account_id=ap_brokerage.id, to_account_id=ap_bank.id,
                            amount_sent=Decimal("150000.00"), fee=Decimal("15.00"), amount_received=Decimal("149985.00"),
                            transfer_method="wire", status="completed"))

        db.add(InvestorAllocation(chain_id=chain2.id, investor_id=lyman.id, source_entity_id=armada_prime.id,
                                  allocation_amount=Decimal("106000.00"), allocation_pct=Decimal("70.6667")))
        db.add(InvestorAllocation(chain_id=chain2.id, investor_id=philip.id, source_entity_id=armada_capital.id,
                                  allocation_amount=Decimal("44000.00"), allocation_pct=Decimal("29.3333")))

        # Pending chain
        chain3 = TransactionChain(
            reference_code="TXN-2026-0003",
            description="GP Distribution - Operating funds transfer",
            original_amount=Decimal("45000.00"), currency="USD",
            source_account_id=ac_bank.id, capital_type="gp_capital", status="pending",
        )
        db.add(chain3)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Seed error (may already exist): {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed on startup
    import app.models  # noqa: F401 - ensure all models are imported
    Base.metadata.create_all(bind=engine)
    seed_if_empty()
    yield


app = FastAPI(title="Capital Tracker API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entities.router)
app.include_router(accounts.router)
app.include_router(investors.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
