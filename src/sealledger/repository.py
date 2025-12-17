import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models_db import LedgerDB, ObligationDB, metadata
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager


def _get_engine():
    url = os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    return create_engine(url, future=True)


def init_db():
    eng = _get_engine()
    metadata.create_all(bind=eng)


@contextmanager
def session_scope():
    eng = _get_engine()
    SessionLocal = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def save_ledger(ledger_id: str, obligations: list, composite: dict, robustness: dict, seals: dict, input_snapshot: dict | None = None):
    with session_scope() as s:
        l = LedgerDB(ledger_id=ledger_id, input_snapshot=input_snapshot, composite=composite, robustness=robustness, seals=seals)
        for ob in obligations:
            o = ObligationDB(obligation_id=ob.get("id", ob.id if hasattr(ob, "id") else None), type=ob.get("type"), owner=ob.get("owner"), constraint=ob.get("constraint"), premises=ob.get("premises"), seal_hash=ob.get("seal_hash"), status=ob.get("status", "unbonded"))
            l.obligations.append(o)
        s.add(l)
        s.flush()
        return l.ledger_id


def get_ledger(ledger_id: str):
    with session_scope() as s:
        return s.query(LedgerDB).filter_by(ledger_id=ledger_id).first()
