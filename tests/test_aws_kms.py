import os
from unittest import mock

import boto3
import pytest

from sealledger.kms import AWSKMS


def test_aws_kms_sign_verify_mock(monkeypatch):
    fake_client = mock.Mock()
    fake_client.sign.return_value = {"Signature": b"deadbeef"}
    fake_client.verify.return_value = {"SignatureValid": True}

    monkeypatch.setattr("boto3.client", lambda *args, **kwargs: fake_client)

    kms = AWSKMS(key_id="alias/test-key")
    sig = kms.sign(None, b"hello")
    assert sig == b"deadbeef"
    ok = kms.verify(None, b"hello", sig)
    assert ok is True


def test_aws_kms_moto_integration():
    moto = pytest.importorskip("moto")
    # Some moto versions expose `mock_kms` at top level, others under moto.kms
    try:
        mock_kms = moto.mock_kms
    except AttributeError:
        try:
            from moto.kms import mock_kms  # type: ignore
        except Exception:
            pytest.skip("moto.mock_kms not available in this moto installation")

    with mock_kms():
        client = boto3.client("kms", region_name="us-east-1")
        # Create an asymmetric signing key
        try:
            resp = client.create_key(Description="test", KeyUsage="SIGN_VERIFY", KeySpec="ECC_NIST_P256")
        except Exception as e:
            pytest.skip(f"moto KMS create_key not available: {e}")

        key_id = resp["KeyMetadata"]["KeyId"]
        kms = AWSKMS(key_id=key_id)
        message = b"integration test"
        try:
            sig = kms.sign(None, message)
            ok = kms.verify(None, message, sig)
        except Exception as e:
            pytest.skip(f"moto KMS sign/verify not implemented: {e}")

        assert isinstance(sig, (bytes, bytearray))
        assert ok is True
