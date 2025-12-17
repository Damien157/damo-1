import os
import json
from typing import Protocol, Tuple
from hashlib import sha256


class StorageInterface(Protocol):
    def upload_snapshot(self, snapshot: dict) -> dict:
        ...


class LocalStorage:
    def __init__(self, dir: str | None = None):
        self.dir = dir or os.getenv("SNAPSHOT_DIR", "snapshots")
        os.makedirs(self.dir, exist_ok=True)

    def upload_snapshot(self, snapshot: dict) -> dict:
        data = json.dumps(snapshot, sort_keys=True).encode()
        h = sha256(data).hexdigest()
        fname = f"snapshot-{h}.json"
        path = os.path.join(self.dir, fname)
        with open(path, "wb") as f:
            f.write(data)
        return {"method": "local", "path": path, "hash": h}


class S3Storage:
    def __init__(self, bucket: str | None = None, endpoint_url: str | None = None):
        import boto3

        self.bucket = bucket or os.getenv("S3_BUCKET", "sealledger")
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    def upload_snapshot(self, snapshot: dict) -> dict:
        import json

        data = json.dumps(snapshot, sort_keys=True).encode()
        h = sha256(data).hexdigest()
        key = f"snapshots/{h}.json"
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
        uri = f"s3://{self.bucket}/{key}"
        return {"method": "s3", "uri": uri, "hash": h}


def get_storage() -> StorageInterface:
    use_s3 = os.getenv("USE_S3", "0") == "1"
    if use_s3:
        return S3Storage()
    return LocalStorage()
