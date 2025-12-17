from .models import PartialSignal, CompositeResult
from .crypto import merkle_root
from typing import List, Dict, Any


class Stitcher:
    def stitch(self, signals: List[PartialSignal]) -> CompositeResult:
        # deterministic order by id
        ordered = sorted(signals, key=lambda s: s.id)
        elements = [str(s.payload).encode() for s in ordered]
        root = merkle_root(elements)
        stitched = {}
        for s in ordered:
            stitched.setdefault(s.source, []).append(s.payload)
        proof = {"merkle_root": root, "count": len(ordered)}
        return CompositeResult(id="C_1", stitched_payload=stitched, proof=proof)
