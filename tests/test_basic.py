from sealledger.obligations import extract_obligations, verify_premises, bond_obligation
from sealledger.crypto import sha256_hex, generate_ed25519_keypair, verify


def test_extract_and_bond():
    data = {"owner": "alice", "portfolio": {"max_loss": 0.1, "loss": 0.05}, "predictions": [0.6, 0.7]}
    obs = extract_obligations(data)
    assert len(obs) >= 1
    ob = next(o for o in obs if o.type == "max_loss")
    premises = verify_premises(ob, data)
    priv, pub = generate_ed25519_keypair()
    ob2 = bond_obligation(ob, premises, priv)
    assert ob2.status == "bonded"
    # verify signature exists in constraint
    assert "_signature" in ob2.constraint
