from typing import List, Dict, Any
from .models import Obligation
from .obligations import verify_premises


class Gate:
    def classify(self, transform: Dict[str, Any], obligations: List[Obligation], inputs: Dict[str, Any]) -> str:
        # simplistic checks: run verify_premises on a simulated transformed input
        simulated = inputs.copy()
        # apply an optional deterministic transform description
        if transform.get("type") == "noop":
            pass
        elif transform.get("type") == "scale_predictions":
            factor = transform.get("factor", 1.0)
            if "predictions" in simulated:
                simulated["predictions"] = [p * factor for p in simulated["predictions"]]

        # evaluate obligations
        any_violation = False
        any_rebond_needed = False
        for ob in obligations:
            p = verify_premises(ob, simulated)
            if not p.get("satisfied", True):
                any_violation = True
            # if transform touches fields relevant to ob, mark rebond needed
            if ob.type in ["prediction_target"] and transform.get("type") == "scale_predictions":
                any_rebond_needed = True

        if any_violation:
            return "RED"
        if any_rebond_needed:
            return "YELLOW"
        return "GREEN"
