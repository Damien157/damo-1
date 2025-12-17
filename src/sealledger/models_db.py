from sqlalchemy import Table, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import registry, relationship
from datetime import datetime

mapper_registry = registry()

metadata = mapper_registry.metadata

ledger_table = Table(
    "ledgers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ledger_id", String, unique=True, nullable=False),
    Column("input_snapshot", JSON, nullable=True),
    Column("composite", JSON, nullable=False),
    Column("robustness", JSON, nullable=False),
    Column("seals", JSON, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

obligation_table = Table(
    "obligations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("obligation_id", String, nullable=False),
    Column("ledger_id", Integer, ForeignKey("ledgers.id", ondelete="CASCADE")),
    Column("type", String, nullable=False),
    Column("owner", String, nullable=True),
    Column("constraint", JSON, nullable=False),
    Column("premises", JSON, nullable=True),
    Column("seal_hash", String, nullable=True),
    Column("status", String, nullable=False, default="unbonded"),
)


class LedgerDB:
    def __init__(self, ledger_id, input_snapshot, composite, robustness, seals, created_at=None):
        self.ledger_id = ledger_id
        self.input_snapshot = input_snapshot
        self.composite = composite
        self.robustness = robustness
        self.seals = seals
        self.created_at = created_at
        self.obligations = []


class ObligationDB:
    def __init__(self, obligation_id, type, owner, constraint, premises=None, seal_hash=None, status="unbonded"):
        self.obligation_id = obligation_id
        self.type = type
        self.owner = owner
        self.constraint = constraint
        self.premises = premises
        self.seal_hash = seal_hash
        self.status = status


mapper_registry.map_imperatively(LedgerDB, ledger_table, properties={"obligations": relationship(ObligationDB, backref="ledger", cascade="all, delete-orphan")})
mapper_registry.map_imperatively(ObligationDB, obligation_table)
