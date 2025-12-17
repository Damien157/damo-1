from sealledger.gate import Gate
from sealledger.obligations import extract_obligations


def test_gate_green():
    data = {"predictions": [0.6, 0.7], "portfolio": {"max_loss": 0.2, "loss": 0.1}}
    g = Gate()
    obs = extract_obligations(data)
    cls = g.classify({"type": "noop"}, obs, data)
    assert cls == "GREEN"


def test_gate_yellow():
    data = {"predictions": [0.6, 0.7]}
    g = Gate()
    obs = extract_obligations(data)
    cls = g.classify({"type": "scale_predictions", "factor": 1.5}, obs, data)
    assert cls in ("YELLOW", "GREEN")


def test_gate_red():
    data = {"portfolio": {"max_loss": 0.05, "loss": 0.1}}
    g = Gate()
    obs = extract_obligations(data)
    cls = g.classify({"type": "noop"}, obs, data)
    assert cls == "RED"
