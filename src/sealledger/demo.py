from .obligations import extract_obligations, verify_premises, bond_obligation
from .crypto import generate_ed25519_keypair
from .gate import Gate
from .stitcher import Stitcher
from .robustness import quantify
from .ledger import ledger
from .models import PartialSignal


def run_full_flow(userdata: dict):
    # extract
    obligations = extract_obligations(userdata)

    # bond all obligations with generated key
    priv, pub = generate_ed25519_keypair()
    for i, ob in enumerate(obligations):
        premises = verify_premises(ob, userdata)
        bond_obligation(ob, premises, priv)

    # transform (noop) and classify
    g = Gate()
    classification = g.classify({"type": "noop"}, obligations, userdata)

    # produce signals (mock)
    signals = [PartialSignal(id="s1", source="src", payload={"k": 1})]
    s = Stitcher().stitch(signals)

    # quantify
    seal_strength = 1.0 if all(getattr(o, "status", None) == "bonded" for o in obligations) else 0.0
    gate_efficacy = 1.0 if classification in ("GREEN", "YELLOW") else 0.0
    robust = quantify(seal_strength, gate_efficacy)

    # seal ledger
    entry = ledger.seal(obligations, s, robust, seals={"pub": pub.hex()}, input_snapshot=userdata)
    return entry
