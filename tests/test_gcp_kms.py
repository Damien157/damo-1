import pytest
from unittest import mock

from sealledger.kms import GCPKMS


def test_gcp_kms_sign_verify_mock(monkeypatch):
    # Mock the kms client
    mock_client = mock.Mock()

    class SigResp:
        signature = b"sigbytes"

    class PubResp:
        pem = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqh...\n-----END PUBLIC KEY-----"

    mock_client.asymmetric_sign.return_value = SigResp()
    mock_client.get_public_key.return_value = PubResp()

    monkeypatch.setattr("sealledger.kms.kms_v1", mock.Mock())
    monkeypatch.setattr("sealledger.kms.kms_v1.KeyManagementServiceClient", lambda *args, **kwargs: mock_client)

    kms = GCPKMS(key_name="projects/x/locations/global/keyRings/r/cryptoKeys/k/cryptoKeyVersions/1")
    msg = b"hello"
    sig = kms.sign(None, msg)
    assert sig == b"sigbytes"
    # verify will try to load the PEM; the mocked PEM above is truncated and will raise -> expect False
    ok = kms.verify(None, msg, sig)
    assert ok is False
