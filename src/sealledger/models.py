from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Obligation(BaseModel):
    id: str
    type: str
    owner: Optional[str]
    constraint: Dict[str, Any]
    premises: Optional[Dict[str, Any]] = None
    seal_hash: Optional[str] = None
    status: str = "unbonded"
    bonded_at: Optional[datetime] = None


class PartialSignal(BaseModel):
    id: str
    source: str
    payload: Dict[str, Any]
    confidence: float = 1.0
    provenance: Dict[str, Any] = Field(default_factory=dict)


class CompositeResult(BaseModel):
    id: str
    stitched_payload: Dict[str, Any]
    proof: Dict[str, Any]
    preserved_obligations: List[str] = Field(default_factory=list)


class RobustnessMetrics(BaseModel):
    seal_strength: float
    gate_efficacy: float
    composite_robustness: float
    confidence: float


class SealedLedger(BaseModel):
    ledger_id: str
    obligations: List[Obligation]
    composite: CompositeResult
    robustness: RobustnessMetrics
    seals: Dict[str, Any]
    input_snapshot: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
