from sealledger.stitcher import Stitcher
from sealledger.models import PartialSignal


def test_stitcher_merkle():
    s = Stitcher()
    signals = [
        PartialSignal(id="a", source="s1", payload={"v": 1}),
        PartialSignal(id="b", source="s2", payload={"v": 2}),
    ]
    comp = s.stitch(signals)
    assert comp.proof["count"] == 2
    assert "merkle_root" in comp.proof
