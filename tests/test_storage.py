import os
from moto import mock_aws as mock_s3
import boto3
from sealledger.storage import S3Storage, LocalStorage, get_storage


def test_local_storage(tmp_path):
    dir = tmp_path / "snapshots"
    s = LocalStorage(dir=str(dir))
    r = s.upload_snapshot({"a": 1})
    assert r["method"] == "local"
    assert "path" in r and r["hash"]


@mock_s3
def test_s3_storage(monkeypatch):
    # set up mock S3
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket = "sealledger"
    s3.create_bucket(Bucket=bucket)
    monkeypatch.setenv("USE_S3", "1")
    monkeypatch.setenv("S3_BUCKET", bucket)
    stor = S3Storage(bucket=bucket)
    r = stor.upload_snapshot({"x": 2})
    assert r["method"] == "s3"
    assert r["uri"].startswith("s3://")


def test_get_storage_default(monkeypatch):
    monkeypatch.delenv("USE_S3", raising=False)
    s = get_storage()
    assert isinstance(s, LocalStorage)
