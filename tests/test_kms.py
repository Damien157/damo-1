from sealledger.kms import LocalKMS


def test_local_kms_sign_and_verify(tmp_path):
    kd = tmp_path / "keys"
    kms = LocalKMS(key_dir=str(kd))
    priv, pub = kms.generate_keypair()
    msg = b"hello"
    sig = kms.sign(None, msg)
    assert kms.verify(None, msg, sig)
