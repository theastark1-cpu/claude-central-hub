"""Seed the database with initial entities, accounts, and investors."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from decimal import Decimal
from app.database import engine, SessionLocal, Base
from app.models import Entity, Account, Investor, TransactionChain, TransferStep, InvestorAllocation
from app.services.audit_service import log_action

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if already seeded
    if db.query(Entity).first():
        print("Database already seeded. Skipping.")
        sys.exit(0)

    # === ENTITIES ===
    armada_prime = Entity(name="Armada Prime LLP", entity_type="llp")
    armada_capital = Entity(name="Armada Capital Group LLP", entity_type="llp")
    royal_kks = Entity(name="Royal KKS", entity_type="group")
    cascade = Entity(name="Cascade", entity_type="group")
    trust_wallets = Entity(name="Individual Trust Wallets", entity_type="trust")
    external = Entity(name="External", entity_type="external")

    for e in [armada_prime, armada_capital, royal_kks, cascade, trust_wallets, external]:
        db.add(e)
    db.flush()

    # === ACCOUNTS ===
    # Armada Prime
    ap_brokerage = Account(entity_id=armada_prime.id, name="Armada Prime Brokerage", account_type="brokerage", provider="Schwab")
    ap_bank = Account(entity_id=armada_prime.id, name="Armada Prime Bank", account_type="bank", provider="Chase", account_number_last4="4521")
    ap_wallet = Account(entity_id=armada_prime.id, name="Armada Prime Trust Wallet", account_type="crypto", provider="Trust Wallet")

    # Armada Capital
    ac_bank = Account(entity_id=armada_capital.id, name="Armada Capital Bank", account_type="bank", provider="Chase", account_number_last4="8832")
    ac_brokerage = Account(entity_id=armada_capital.id, name="Armada Capital Brokerage", account_type="brokerage", provider="Schwab")

    # Royal KKS
    rkks_coinbase = Account(entity_id=royal_kks.id, name="Royal KKS Coinbase", account_type="crypto", provider="Coinbase")
    rkks_bank = Account(entity_id=royal_kks.id, name="Royal KKS Bank", account_type="bank", provider="Wells Fargo")

    # Cascade
    cascade_bank = Account(entity_id=cascade.id, name="Cascade Bank", account_type="bank", provider="Bank of America")

    # Trust Wallets
    tw_1 = Account(entity_id=trust_wallets.id, name="Trust Wallet Alpha", account_type="crypto", provider="Trust Wallet")
    tw_2 = Account(entity_id=trust_wallets.id, name="Trust Wallet Beta", account_type="crypto", provider="Trust Wallet")

    # External
    ext_recipient = Account(entity_id=external.id, name="External Recipient", account_type="bank", is_external=True)
    ext_crypto = Account(entity_id=external.id, name="External Crypto Wallet", account_type="crypto", is_external=True)

    accounts = [ap_brokerage, ap_bank, ap_wallet, ac_bank, ac_brokerage, rkks_coinbase, rkks_bank, cascade_bank, tw_1, tw_2, ext_recipient, ext_crypto]
    for a in accounts:
        db.add(a)
    db.flush()

    # === INVESTORS ===
    investors = [
        Investor(name="Lyman Phillips", email="lyman@example.com"),
        Investor(name="Philip Okala", email="pokala@example.com"),
        Investor(name="NC Opportunity Fund, LP"),
        Investor(name="Sarah Martinez", email="smartinez@example.com"),
        Investor(name="David Chen", email="dchen@example.com"),
        Investor(name="Apex Holdings LLC"),
        Investor(name="Robert Williams", email="rwilliams@example.com"),
        Investor(name="Jennifer Park", email="jpark@example.com"),
    ]
    for inv in investors:
        db.add(inv)
    db.flush()

    lyman = investors[0]
    philip = investors[1]

    # === SAMPLE TRANSACTION: Lyman Phillips $106,000 flow ===
    chain = TransactionChain(
        reference_code="TXN-2026-0001",
        description="Lyman Phillips withdrawal - Brokerage to external via crypto",
        original_amount=Decimal("106000.00"),
        currency="USD",
        source_account_id=ap_brokerage.id,
        destination_account_id=ext_recipient.id,
        capital_type="lp_capital",
        status="completed",
        total_fees=Decimal("5.00"),
        final_amount=Decimal("105995.00"),
    )
    db.add(chain)
    db.flush()

    # Step 1: Brokerage → Bank (wire fee $2)
    step1 = TransferStep(
        chain_id=chain.id, step_order=1,
        from_account_id=ap_brokerage.id, to_account_id=ap_bank.id,
        amount_sent=Decimal("106000.00"), fee=Decimal("2.00"), amount_received=Decimal("105998.00"),
        transfer_method="wire", status="completed",
    )
    # Step 2: Bank → Crypto Wallet (ACH fee $3)
    step2 = TransferStep(
        chain_id=chain.id, step_order=2,
        from_account_id=ap_bank.id, to_account_id=ap_wallet.id,
        amount_sent=Decimal("105998.00"), fee=Decimal("3.00"), amount_received=Decimal("105995.00"),
        transfer_method="ach", status="completed",
    )
    # Step 3: Crypto Wallet → External (no fee)
    step3 = TransferStep(
        chain_id=chain.id, step_order=3,
        from_account_id=ap_wallet.id, to_account_id=ext_recipient.id,
        amount_sent=Decimal("105995.00"), fee=Decimal("0.00"), amount_received=Decimal("105995.00"),
        transfer_method="blockchain", status="completed",
    )
    for s in [step1, step2, step3]:
        db.add(s)
    db.flush()

    # Allocation: 100% to Lyman Phillips
    alloc1 = InvestorAllocation(
        chain_id=chain.id, investor_id=lyman.id, source_entity_id=armada_prime.id,
        allocation_amount=Decimal("106000.00"), allocation_pct=Decimal("100.0000"),
    )
    db.add(alloc1)

    # === SAMPLE TRANSACTION: Split transaction $150,000 ===
    chain2 = TransactionChain(
        reference_code="TXN-2026-0002",
        description="Split withdrawal - Lyman Phillips + Armada Capital allocation",
        original_amount=Decimal("150000.00"),
        currency="USD",
        source_account_id=ap_brokerage.id,
        capital_type="lp_capital",
        status="in_transit",
        total_fees=Decimal("15.00"),
    )
    db.add(chain2)
    db.flush()

    step2_1 = TransferStep(
        chain_id=chain2.id, step_order=1,
        from_account_id=ap_brokerage.id, to_account_id=ap_bank.id,
        amount_sent=Decimal("150000.00"), fee=Decimal("15.00"), amount_received=Decimal("149985.00"),
        transfer_method="wire", status="completed",
    )
    db.add(step2_1)
    db.flush()

    # Split allocations
    alloc2a = InvestorAllocation(
        chain_id=chain2.id, investor_id=lyman.id, source_entity_id=armada_prime.id,
        allocation_amount=Decimal("106000.00"), allocation_pct=Decimal("70.6667"),
    )
    alloc2b = InvestorAllocation(
        chain_id=chain2.id, investor_id=philip.id, source_entity_id=armada_capital.id,
        allocation_amount=Decimal("44000.00"), allocation_pct=Decimal("29.3333"),
    )
    db.add(alloc2a)
    db.add(alloc2b)

    # === SAMPLE TRANSACTION: Pending GP distribution ===
    chain3 = TransactionChain(
        reference_code="TXN-2026-0003",
        description="GP Distribution - Operating funds transfer",
        original_amount=Decimal("45000.00"),
        currency="USD",
        source_account_id=ac_bank.id,
        capital_type="gp_capital",
        status="pending",
    )
    db.add(chain3)

    db.commit()
    print("Database seeded successfully!")
    print(f"  - {db.query(Entity).count()} entities")
    print(f"  - {len(accounts)} accounts")
    print(f"  - {len(investors)} investors")
    print(f"  - 3 transaction chains (1 completed, 1 in-transit, 1 pending)")

finally:
    db.close()
