import os
import time

import boto3
import pytest

from sealledger.kms import AWSKMS


def test_aws_kms_localstack_integration():
    # This test requires LocalStack (KMS) available and the env var AWS_KMS_ENDPOINT set
    endpoint = os.getenv("AWS_KMS_ENDPOINT")
    if not endpoint:
        pytest.skip("AWS_KMS_ENDPOINT not set; skipping LocalStack KMS integration test")

    # Create a boto3 client pointing to localstack
    client = boto3.client(
        "kms",
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    # LocalStack sometimes takes a moment to be fully ready
    for _ in range(10):
        try:
            client.list_keys()
            break
        except Exception:
            time.sleep(1)
    else:
        pytest.skip("LocalStack KMS not reachable")

    # Create an asymmetric key suitable for sign/verify
    resp = client.create_key(Description="test-key", KeyUsage="SIGN_VERIFY", KeySpec="ECC_NIST_P256")
    key_id = resp["KeyMetadata"]["KeyId"]

    # Use our AWSKMS implementation against localstack
    os.environ.setdefault("AWS_KMS_ENDPOINT", endpoint)
    kms = AWSKMS(key_id=key_id)

    msg = b"localstack integration"
    sig = kms.sign(None, msg)
    assert isinstance(sig, (bytes, bytearray))
    ok = kms.verify(None, msg, sig)
    assert ok is True
