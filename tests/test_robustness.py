from sealledger.robustness import quantify


def test_quantify_simple():
    r = quantify(1.0, 1.0, confidence=1.0)
    assert r.composite_robustness >= 0.0
    assert r.seal_strength == 1.0
