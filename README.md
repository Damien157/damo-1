# damo-1

SealedLedger prototype: minimal implementation of obligations extraction, bonding, gate classification, stitcher, robustness quantification, and an append-only in-memory ledger.

Quickstart

- Install dependencies (poetry recommended):
  - poetry install
- Run the app:
  - poetry run uvicorn app.main:app --reload
  - or (without poetry): uvicorn app.main:app --reload
- Run tests:
  - poetry run pytest

Security & Anchoring

- Seals use Ed25519 signatures (via the cryptography library).
- Anchoring is prototyped via a local timestamp; replace with RFC-3161 TSA or on-chain anchoring for production.
- Use an HSM or cloud KMS for production signing keys.

Quick demo

- Run the demo script:
  - python scripts/run_demo.py

Deployment

- A minimal Dockerfile is provided to run the FastAPI app.
- CI is configured with GitHub Actions to run tests, alembic migrations, and build a Docker image. See `.github/workflows/ci.yml`.


KMS Integration Tests (LocalStack) 🔧

This project includes an optional integration test that exercises AWS KMS sign/verify operations against LocalStack. The test is gated and skips when LocalStack isn't configured.

How to run locally:

- Start LocalStack with the KMS service (docker or docker-compose). Example (docker):

  docker run --rm -p 4566:4566 -e SERVICES=kms localstack/localstack:latest

- Export the LocalStack endpoint and AWS creds (these values are used by the tests):

  export AWS_KMS_ENDPOINT=http://localhost:4566
  export AWS_ACCESS_KEY_ID=test
  export AWS_SECRET_ACCESS_KEY=test
  export AWS_REGION=us-east-1

- Run the single test:

  pytest -q tests/test_aws_kms_localstack.py

How to run in CI:

- A manual, gated GitHub Actions workflow is provided at `.github/workflows/kms-integration.yml`.
- You can trigger it via the Actions tab (workflow name: "AWS KMS Integration (LocalStack)"). It also runs weekly and on pull requests to `main`.

Notes:

- The workflow uses LocalStack as a service and runs only when manually dispatched, on PRs to `main`, or weekly on Sundays (UTC).
- Tests are skipped automatically if LocalStack isn't available, so CI for normal PRs remains fast and stable.



