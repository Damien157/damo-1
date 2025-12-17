#!/usr/bin/env python3
from sealledger.demo import run_full_flow
import json


def main():
    data = {"owner": "demo", "portfolio": {"max_loss": 0.2, "loss": 0.1}, "predictions": [0.6, 0.7]}
    entry = run_full_flow(data)
    print("Sealed ledger id:", entry.ledger_id)
    print(json.dumps(entry.dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
