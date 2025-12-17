from .models import RobustnessMetrics
from typing import List


def quantify(seal_strength: float, gate_efficacy: float, confidence: float = 1.0, alpha=0.5, beta=0.3, gamma=0.2):
    # weighted linear aggregation
    r = alpha * seal_strength + beta * gate_efficacy + gamma * confidence
    return RobustnessMetrics(
        seal_strength=seal_strength,
        gate_efficacy=gate_efficacy,
        composite_robustness=r,
        confidence=confidence,
    )
