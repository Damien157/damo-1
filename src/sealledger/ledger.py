from .models import SealedLedger, Obligation, CompositeResult, RobustnessMetrics
from datetime import datetime
from typing import Dict, Any, List
from .timestamp import get_provider
from .storage import get_storage


class InMemoryLedger:
    def __init__(self):
        self._store: Dict[str, SealedLedger] = {}
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"{self._counter:03d}"

    def seal(self, obligations: List[Obligation], composite: CompositeResult, robustness: RobustnessMetrics, seals: Dict[str, Any], input_snapshot: Dict[str, Any] | None = None) -> SealedLedger:
        lid = self._next_id()
        entry = SealedLedger(
            ledger_id=lid,
            obligations=obligations,
            composite=composite,
            robustness=robustness,
            seals=seals,
            input_snapshot=input_snapshot,
            created_at=datetime.utcnow(),
        )
        # store input snapshot via storage adapter (S3 or local) to keep ledgers small
        try:
            if entry.input_snapshot is not None:
                store = get_storage()
                uploaded = store.upload_snapshot(entry.input_snapshot)
                # replace input snapshot with a pointer
                entry.input_snapshot = {"pointer": uploaded}
                entry.seals = {**(entry.seals or {}), "snapshot": uploaded}
        except Exception:
            pass

        # anchor the sealed ledger using configured timestamp provider
        try:
            prov = get_provider()
            import json

            data = json.dumps(entry.model_dump(), sort_keys=True).encode()
            anchor = prov.anchor(data)
            entry.seals = {**(entry.seals or {}), "anchor": anchor}
        except Exception:
            # fallback: keep existing seals and continue (don't fail sealing in prototype)
            pass

        self._store[lid] = entry
        return entry

    def get(self, ledger_id: str) -> SealedLedger:
        return self._store[ledger_id]


ledger = InMemoryLedger()
